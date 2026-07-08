import os
import random
import numpy as np
import pandas as pd
import scipy.stats
import scipy.signal
import matplotlib.pyplot as plt
from pathlib import Path

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

import tensorflow as tf
tf.random.set_seed(42)
tf.config.set_visible_devices([], 'GPU') # Run on CPU for stability and predictability

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score, accuracy_score

def resample_trajectory(series, target_len=100):
    original_x = np.linspace(0, 1, len(series))
    new_x = np.linspace(0, 1, target_len)
    return np.interp(new_x, original_x, series)

def normalize_scheme_a(traj):
    # Offset-subtracted
    return traj - traj[0]

def normalize_scheme_b(traj):
    # Min-max shape-only
    rng = np.max(traj) - np.min(traj)
    if rng < 1e-5:
        return np.zeros_like(traj)
    return (traj - np.min(traj)) / rng

def extract_shape_features(resampled):
    # resampled is a 100-point normalized array (Scheme B)
    # Peak index is the minimum value (included angle convention, peak flexion = min angle)
    idx_peak = np.argmin(resampled)
    if idx_peak <= 1:
        idx_peak = 2
    if idx_peak >= 98:
        idx_peak = 97
        
    t_descent = idx_peak
    t_ascent = 99 - idx_peak
    
    # 1. Descent-to-ascent duration ratio
    ratio = t_descent / max(t_ascent, 1)
    
    # 2. Trajectory asymmetry index
    descent_curve = resampled[:idx_peak+1]
    ascent_curve = resampled[idx_peak:]
    descent_50 = np.interp(np.linspace(0, 1, 50), np.linspace(0, 1, len(descent_curve)), descent_curve)
    ascent_50 = np.interp(np.linspace(0, 1, 50), np.linspace(0, 1, len(ascent_curve)), ascent_curve)
    asymmetry = np.mean(np.abs(descent_50 - ascent_50[::-1]))
    
    # 3. Normalized time-to-peak flexion
    time_to_peak = idx_peak / 99.0
    
    # 4. Descent velocity skewness
    vel_descent = np.diff(descent_curve)
    if len(vel_descent) > 2:
        skew_descent = scipy.stats.skew(vel_descent)
    else:
        skew_descent = 0.0
        
    # 5. Ascent velocity skewness
    vel_ascent = np.diff(ascent_curve)
    if len(vel_ascent) > 2:
        skew_ascent = scipy.stats.skew(vel_ascent)
    else:
        skew_ascent = 0.0
        
    # 6. Descent curve concavity (relative to linear interpolation)
    concavity = np.mean(descent_50 - np.linspace(descent_50[0], descent_50[-1], 50))
    
    return [ratio, asymmetry, time_to_peak, skew_descent, skew_ascent, concavity]

def load_dataset(modality):
    project_root = Path(".")
    if modality == 'squat':
        bio_path = project_root / "14_rehab24_outputs" / "biomarkers_per_rep" / "rehab24_squat_per_rep_biomarkers.csv"
        traj_dir = project_root / "14_rehab24_outputs" / "smoothed_per_rep"
    else: # lunge
        bio_path = project_root / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"
        traj_dir = project_root / "15_rehab24_lunge_outputs" / "smoothed_per_rep"
        
    df_bio = pd.read_csv(bio_path)
    if modality == 'lunge':
        df_bio = df_bio[df_bio['phase_identification_status'] == 'ok'].copy()
        
    reps_data = []
    
    for idx, row in df_bio.iterrows():
        vid = row['video_id']
        rep_num = int(row['rep_number'])
        label = int(row['correctness_label'])
        sub_id = int(row['subject_id'])
        peak_flexion = float(row['peak_flexion_deg'])
        
        filename = f"{vid}_rep_{rep_num:02d}_smoothed.csv"
        file_path = traj_dir / filename
        
        if not file_path.is_file():
            print(f"Warning: File not found {file_path}")
            continue
            
        df_traj = pd.read_csv(file_path)
        y = df_traj['knee_angle_smoothed'].interpolate(method='linear').ffill().bfill().values
        
        # Resample to 100 points
        y_100 = resample_trajectory(y, target_len=100)
        
        # Normalization Schemes
        y_a = normalize_scheme_a(y_100)
        y_b = normalize_scheme_b(y_100)
        
        # Extract features (Scheme B is pure shape-only, Scheme A is shape + preserved amplitude)
        feat_a = extract_shape_features(normalize_scheme_b(y_a))
        feat_b = extract_shape_features(y_b)
        
        reps_data.append({
            'subject_id': sub_id,
            'label': label,
            'peak_flexion': peak_flexion,
            'traj_raw': y_100,
            'traj_a': y_a,
            'traj_b': y_b,
            'features_a': feat_a,
            'features_b': feat_b
        })
        
    print(f"Loaded {len(reps_data)} processed reps for {modality}.")
    return reps_data

def build_lstm_model():
    model = Sequential([
        LSTM(8, input_shape=(100, 1), recurrent_dropout=0.3, dropout=0.3),
        Dense(4, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model

def run_loso(dataset, modality, scheme_name):
    # Extract unique subjects
    subjects = sorted(list(set([x['subject_id'] for x in dataset])))
    n_folds = len(subjects)
    
    # Store predictions for pooled metrics
    pooled_y_true = []
    pooled_naive_pred = []
    pooled_peak_prob = []
    pooled_shape_prob = []
    pooled_lstm_prob = []
    
    # Store per-fold accuracies
    fold_results = []
    
    # Determine trajectory key and feature key based on scheme
    # Note: shape features are extracted from min-max scaled shape, which is amplitude-invariant.
    # Scheme A keeps amplitude for the raw LSTM trajectory (offset-subtracted).
    # Scheme B is pure shape for both.
    traj_key = 'traj_a' if scheme_name == 'Scheme_A' else 'traj_b'
    feat_key = 'features_a' if scheme_name == 'Scheme_A' else 'features_b'
    
    # Class majority baseline guess for the entire modality
    all_labels = [x['label'] for x in dataset]
    majority_class = scipy.stats.mode(all_labels, keepdims=True).mode[0]
    
    for fold_idx, test_sub in enumerate(subjects):
        # Split train and test
        train_data = [x for x in dataset if x['subject_id'] != test_sub]
        test_data = [x for x in dataset if x['subject_id'] == test_sub]
        
        y_train = np.array([x['label'] for x in train_data])
        y_test = np.array([x['label'] for x in test_data])
        
        # 1. Naive baseline predictions
        train_majority = scipy.stats.mode(y_train, keepdims=True).mode[0]
        y_pred_naive = np.full_like(y_test, train_majority)
        
        # 2. Peak Flexion Baseline
        X_train_peak = np.array([x['peak_flexion'] for x in train_data]).reshape(-1, 1)
        X_test_peak = np.array([x['peak_flexion'] for x in test_data]).reshape(-1, 1)
        
        scaler_peak = StandardScaler()
        X_train_peak_s = scaler_peak.fit_transform(X_train_peak)
        X_test_peak_s = scaler_peak.transform(X_test_peak)
        
        clf_peak = LogisticRegression(class_weight='balanced', C=1.0, random_state=42)
        clf_peak.fit(X_train_peak_s, y_train)
        y_prob_peak = clf_peak.predict_proba(X_test_peak_s)[:, 1]
        
        # 3. Shape Feature Baseline
        X_train_shape = np.array([x[feat_key] for x in train_data])
        X_test_shape = np.array([x[feat_key] for x in test_data])
        
        scaler_shape = StandardScaler()
        X_train_shape_s = scaler_shape.fit_transform(X_train_shape)
        X_test_shape_s = scaler_shape.transform(X_test_shape)
        
        clf_shape = LogisticRegression(class_weight='balanced', C=0.5, random_state=42)
        clf_shape.fit(X_train_shape_s, y_train)
        y_prob_shape = clf_shape.predict_proba(X_test_shape_s)[:, 1]
        
        # 4. LSTM Model
        X_train_lstm = np.array([x[traj_key] for x in train_data]).reshape(-1, 100, 1)
        X_test_lstm = np.array([x[traj_key] for x in test_data]).reshape(-1, 100, 1)
        
        # Compute class weights for training
        c0 = np.sum(y_train == 0)
        c1 = np.sum(y_train == 1)
        total = len(y_train)
        class_weight = {0: total / (2.0 * max(c0, 1)), 1: total / (2.0 * max(c1, 1))}
        
        # Re-seed TF graph for predictability within fold
        tf.random.set_seed(42 + fold_idx)
        lstm = build_lstm_model()
        
        # Early stopping on a small random subset of train as validation
        # Since we cannot leak test subject, we split training set 80/20 at repetition level for early stopping validation
        val_idx = int(0.2 * len(X_train_lstm))
        if val_idx >= 5:
            # Shuffle training set indexes
            shuffled_indices = np.random.permutation(len(X_train_lstm))
            t_idx = shuffled_indices[val_idx:]
            v_idx = shuffled_indices[:val_idx]
            
            X_tr, y_tr = X_train_lstm[t_idx], y_train[t_idx]
            X_val, y_val = X_train_lstm[v_idx], y_train[v_idx]
        else:
            X_tr, y_tr = X_train_lstm, y_train
            X_val, y_val = X_train_lstm, y_train
            
        early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
        lstm.fit(X_tr, y_tr,
                 validation_data=(X_val, y_val),
                 epochs=100,
                 batch_size=8,
                 class_weight=class_weight,
                 callbacks=[early_stop],
                 verbose=0)
                 
        y_prob_lstm = lstm.predict(X_test_lstm, verbose=0).flatten()
        
        # Save predicted probabilities and true targets
        pooled_y_true.extend(y_test)
        pooled_naive_pred.extend(y_pred_naive)
        pooled_peak_prob.extend(y_prob_peak)
        pooled_shape_prob.extend(y_prob_shape)
        pooled_lstm_prob.extend(y_prob_lstm)
        
        # Fold-level accuracies
        acc_naive = accuracy_score(y_test, y_pred_naive)
        acc_peak = accuracy_score(y_test, y_prob_peak > 0.5)
        acc_shape = accuracy_score(y_test, y_prob_shape > 0.5)
        acc_lstm = accuracy_score(y_test, y_prob_lstm > 0.5)
        
        fold_results.append({
            'fold': fold_idx + 1,
            'subject_id': test_sub,
            'n_reps': len(y_test),
            'n_correct': np.sum(y_test == 1),
            'n_incorrect': np.sum(y_test == 0),
            'acc_naive': acc_naive,
            'acc_peak': acc_peak,
            'acc_shape': acc_shape,
            'acc_lstm': acc_lstm
        })
        
    # Compute Pooled Global Metrics
    pooled_y_true = np.array(pooled_y_true)
    pooled_naive_pred = np.array(pooled_naive_pred)
    pooled_peak_pred = (np.array(pooled_peak_prob) > 0.5).astype(int)
    pooled_shape_pred = (np.array(pooled_shape_prob) > 0.5).astype(int)
    pooled_lstm_pred = (np.array(pooled_lstm_prob) > 0.5).astype(int)
    
    # Check if we have class variance in pooled targets
    has_variance = len(np.unique(pooled_y_true)) > 1
    
    global_results = {
        'accuracy': {
            'naive': accuracy_score(pooled_y_true, pooled_naive_pred),
            'peak': accuracy_score(pooled_y_true, pooled_peak_pred),
            'shape': accuracy_score(pooled_y_true, pooled_shape_pred),
            'lstm': accuracy_score(pooled_y_true, pooled_lstm_pred),
        },
        'balanced_acc': {
            'naive': balanced_accuracy_score(pooled_y_true, pooled_naive_pred) if has_variance else 0.5,
            'peak': balanced_accuracy_score(pooled_y_true, pooled_peak_pred) if has_variance else 0.5,
            'shape': balanced_accuracy_score(pooled_y_true, pooled_shape_pred) if has_variance else 0.5,
            'lstm': balanced_accuracy_score(pooled_y_true, pooled_lstm_pred) if has_variance else 0.5,
        },
        'f1': {
            'naive': f1_score(pooled_y_true, pooled_naive_pred, zero_division=0) if has_variance else 0.0,
            'peak': f1_score(pooled_y_true, pooled_peak_pred, zero_division=0) if has_variance else 0.0,
            'shape': f1_score(pooled_y_true, pooled_shape_pred, zero_division=0) if has_variance else 0.0,
            'lstm': f1_score(pooled_y_true, pooled_lstm_pred, zero_division=0) if has_variance else 0.0,
        },
        'auc': {
            'naive': 0.5,
            'peak': roc_auc_score(pooled_y_true, pooled_peak_prob) if has_variance else 0.5,
            'shape': roc_auc_score(pooled_y_true, pooled_shape_prob) if has_variance else 0.5,
            'lstm': roc_auc_score(pooled_y_true, pooled_lstm_prob) if has_variance else 0.5,
        }
    }
    
    return fold_results, global_results

def main():
    print("=================================================================")
    print("Starting Phase 12 - Temporal Sequence Model Evaluation (Track B)")
    print("=================================================================")
    
    # 1. Load both cohorts
    squat_data = load_dataset('squat')
    lunge_data = load_dataset('lunge')
    
    results_dir = Path("23_temporal_model_outputs")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    modalities = {
        'squat': squat_data,
        'lunge': lunge_data
    }
    
    schemes = ['Scheme_A', 'Scheme_B']
    
    summary_rows = []
    
    # Execute LOSO cross validation for all permutations
    for mod_name, mod_data in modalities.items():
        for scheme in schemes:
            print(f"\nEvaluating LOSO Cross Validation: {mod_name.upper()} | {scheme}")
            fold_res, glob_res = run_loso(mod_data, mod_name, scheme)
            
            # Save fold-level results to CSV
            df_folds = pd.DataFrame(fold_res)
            folds_csv_path = results_dir / f"{mod_name}_{scheme}_folds.csv"
            df_folds.round(4).to_csv(folds_csv_path, index=False)
            print(f"Saved per-fold results to {folds_csv_path}")
            
            # Add to main summary table
            for model_type in ['naive', 'peak', 'shape', 'lstm']:
                summary_rows.append({
                    'Modality': mod_name,
                    'Scheme': scheme,
                    'Model': model_type,
                    'Global_Accuracy': glob_res['accuracy'][model_type],
                    'Global_Balanced_Accuracy': glob_res['balanced_acc'][model_type],
                    'Global_F1': glob_res['f1'][model_type],
                    'Global_AUC': glob_res['auc'][model_type],
                })
                
    df_summary = pd.DataFrame(summary_rows)
    summary_csv_path = results_dir / "temporal_model_comparison.csv"
    df_summary.round(4).to_csv(summary_csv_path, index=False)
    print(f"\nSaved global comparison table to {summary_csv_path}")
    
    # 2. Write Markdown comparison report
    report_content = f"""# Phase 12 — Temporal Sequence Model Evaluation Report

This report summarizes the Leave-One-Subject-Out (LOSO) cross-validation results for squats ($N=98$ reps, 9 subjects) and lunges ($N=61$ reps, 7 subjects) under two normalization configurations:
*   **Scheme A (Offset Subtraction):** $\\theta(t) - \\theta(0)$ (neutralizes perspective bias while keeping amplitude).
*   **Scheme B (Min-Max Shape):** scales between $0.0$ and $1.0$ (isolates trajectory timing/shape and ignores amplitude).

---

## 1. Global Comparison Summary Table

| Modality | Normalization | Model | Accuracy | Balanced Accuracy | F1-Score | AUC-ROC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for idx, row in df_summary.iterrows():
        report_content += f"| {row['Modality'].upper()} | {row['Scheme']} | **{row['Model']}** | {row['Global_Accuracy']:.4f} | {row['Global_Balanced_Accuracy']:.4f} | {row['Global_F1']:.4f} | {row['Global_AUC']:.4f} |\n"
        
    report_content += """
*Note: The **naive** baseline guesses the global training majority class (Squat: Correct (73.47%), Lunge: Incorrect (59.02%)).*

---

## 2. Per-Fold Classifier Accuracy Analysis

This section logs the repetition counts, class splits, and the specific classification accuracies achieved when testing on each individual subject.
"""
    for mod_name in ['squat', 'lunge']:
        for scheme in schemes:
            report_content += f"\n### {mod_name.upper()} | {scheme} — Fold-by-Fold Test Accuracy\n\n"
            report_content += "| Fold | Test Subject | Reps | Correct | Incorrect | Naive | Peak Flexion | Shape Baseline | LSTM |\n"
            report_content += "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
            
            df_f = pd.read_csv(results_dir / f"{mod_name}_{scheme}_folds.csv")
            for idx, r in df_f.iterrows():
                report_content += f"| {int(r['fold'])} | Subject {int(r['subject_id'])} | {int(r['n_reps'])} | {int(r['n_correct'])} | {int(r['n_incorrect'])} | {r['acc_naive']:.4f} | {r['acc_peak']:.4f} | {r['acc_shape']:.4f} | {r['acc_lstm']:.4f} |\n"
            
            # Add mean and standard deviation rows
            report_content += f"| **Mean** | — | — | — | — | **{df_f['acc_naive'].mean():.4f}** | **{df_f['acc_peak'].mean():.4f}** | **{df_f['acc_shape'].mean():.4f}** | **{df_f['acc_lstm'].mean():.4f}** |\n"
            report_content += f"| **SD** | — | — | — | — | {df_f['acc_naive'].std():.4f} | {df_f['acc_peak'].std():.4f} | {df_f['acc_shape'].std():.4f} | {df_f['acc_lstm'].std():.4f} |\n"
            
    report_content_path = results_dir / "temporal_model_evaluation_report.md"
    report_content_path.write_text(report_content, encoding='utf-8')
    print(f"Saved evaluation markdown report to {report_content_path}")
    
    # 3. Generate Evaluation Plot
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    
    # Plot squat performance
    ax = axes[0]
    df_sq = df_summary[df_summary['Modality'] == 'squat']
    x = np.arange(4)
    width = 0.35
    
    rects1 = ax.bar(x - width/2, df_sq[df_sq['Scheme'] == 'Scheme_A']['Global_Balanced_Accuracy'], width, label='Scheme A (Offset Preserved)', color='#1f77b4')
    rects2 = ax.bar(x + width/2, df_sq[df_sq['Scheme'] == 'Scheme_B']['Global_Balanced_Accuracy'], width, label='Scheme B (Min-Max Shape)', color='#ff7f0e')
    
    ax.axhline(y=0.7347, color='r', linestyle='--', alpha=0.7, label='Majority-Class floor (73.47%)')
    ax.set_ylabel('Global Balanced Accuracy')
    ax.set_title('Squat Form Classification Performance (9 Folds LOSO)')
    ax.set_xticks(x)
    ax.set_xticklabels(['Naive (Majority)', 'Peak Flexion', 'Shape Baseline', 'LSTM'])
    ax.set_ylim(0, 1.05)
    ax.legend(loc='lower left')
    
    # Plot lunge performance
    ax = axes[1]
    df_lg = df_summary[df_summary['Modality'] == 'lunge']
    
    rects3 = ax.bar(x - width/2, df_lg[df_lg['Scheme'] == 'Scheme_A']['Global_Balanced_Accuracy'], width, label='Scheme A (Offset Preserved)', color='#1f77b4')
    rects4 = ax.bar(x + width/2, df_lg[df_lg['Scheme'] == 'Scheme_B']['Global_Balanced_Accuracy'], width, label='Scheme B (Min-Max Shape)', color='#ff7f0e')
    
    ax.axhline(y=0.5902, color='r', linestyle='--', alpha=0.7, label='Majority-Class floor (59.02%)')
    ax.set_title('Lunge Form Classification Performance (7 Folds LOSO)')
    ax.set_xticks(x)
    ax.set_xticklabels(['Naive (Majority)', 'Peak Flexion', 'Shape Baseline', 'LSTM'])
    ax.legend(loc='lower left')
    
    plt.tight_layout()
    plot_path = results_dir / "temporal_model_performance_comparison.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved performance comparison figure to {plot_path}")
    
    print("\n=================================================================")
    print("Phase 12 Evaluation Completed successfully.")
    print("=================================================================")

if __name__ == "__main__":
    main()
