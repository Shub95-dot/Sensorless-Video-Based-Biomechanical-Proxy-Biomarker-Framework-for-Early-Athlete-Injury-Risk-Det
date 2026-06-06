"""Surgical correction to Phase 4G rep classification outputs.

Manual override of four false-positive multi-rep classifications
based on visual review of the rep-segmentation plots.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Define paths
ROOT = Path(__file__).resolve().parent.parent
squats_rep_summary_path = ROOT / "4_pose_outputs" / "temporal" / "squats_rep_summary.csv"
squats_biomarkers_path = ROOT / "4_pose_outputs" / "temporal" / "squats_biomarkers.csv"
phase4g_summary_path = ROOT / "4_pose_outputs" / "temporal" / "phase4g_rep_segmentation_summary.txt"

# Helper to detect separator
def detect_separator(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline()
    if ';' in first_line:
        return ';'
    elif '\t' in first_line:
        return '\t'
    else:
        return ','

def main():
    # Read files
    sep_rep_summary = detect_separator(squats_rep_summary_path)
    df_rep = pd.read_csv(squats_rep_summary_path, sep=None, engine='python')
    df_bio = pd.read_csv(squats_biomarkers_path, sep=None, engine='python')

    # Target subjects
    target_subjects = [1682, 1774, 1823, 1884]

    # Ensure we print the original values for the sanity checkpoint
    original_info = {}
    for sub in target_subjects:
        # Locate row in df_rep
        row_rep = df_rep[df_rep['Subject_ID'] == sub]
        if row_rep.empty:
            raise ValueError(f"Subject {sub} not found in squats_rep_summary.csv")
        original_info[sub] = {
            'rep_classification': row_rep.iloc[0]['rep_classification'],
            'rep_count': int(row_rep.iloc[0]['rep_count'])
        }

    # Apply changes to squats_rep_summary.csv
    for sub in target_subjects:
        # Get values from squats_biomarkers.csv
        row_bio = df_bio[df_bio['Subject_ID'] == sub]
        if row_bio.empty:
            raise ValueError(f"Subject {sub} not found in squats_biomarkers.csv")
        
        peak_flexion_deg = row_bio.iloc[0]['peak_flexion_deg']
        rom_deg = row_bio.iloc[0]['rom_deg']
        tempo_ratio = row_bio.iloc[0]['tempo_ratio']
        
        # Update df_rep
        idx = df_rep[df_rep['Subject_ID'] == sub].index[0]
        df_rep.at[idx, 'rep_classification'] = 'single_rep'
        df_rep.at[idx, 'rep_count'] = 1
        
        df_rep.at[idx, 'peak_flexion_cv'] = np.nan
        df_rep.at[idx, 'rom_cv'] = np.nan
        df_rep.at[idx, 'tempo_ratio_cv'] = np.nan
        
        df_rep.at[idx, 'peak_flexion_std'] = np.nan
        df_rep.at[idx, 'rom_std'] = np.nan
        df_rep.at[idx, 'tempo_ratio_std'] = np.nan
        
        df_rep.at[idx, 'peak_flexion_mean'] = peak_flexion_deg
        df_rep.at[idx, 'rom_mean'] = rom_deg
        df_rep.at[idx, 'tempo_ratio_mean'] = tempo_ratio

    # Make sure rep_count values are integers
    df_rep['rep_count'] = df_rep['rep_count'].astype(int)

    # Print sanity checkpoint to stdout BEFORE saving
    print("Subjects reclassified to single_rep:")
    for sub in target_subjects:
        orig = original_info[sub]
        print(f"  {sub}  rep_classification: {orig['rep_classification']} -> single_rep   rep_count: {orig['rep_count']} -> 1")
    print()

    single_rep_count = int((df_rep['rep_classification'] == 'single_rep').sum())
    multi_rep_count = int((df_rep['rep_classification'] == 'multi_rep').sum())
    total_count = len(df_rep)

    print("Updated cohort classification counts:")
    print(f"  single_rep : {single_rep_count}  (expected: 10)")
    print(f"  multi_rep  : {multi_rep_count}  (expected: 0)")
    print(f"  total      : {total_count}  (expected: 10)")
    print()

    # Check counts
    if single_rep_count != 10 or multi_rep_count != 0 or total_count != 10:
        print("CRITICAL ERROR: Updated counts do not match expectations. Aborting write operation!")
        sys.exit(1)

    # Write updated rep summary back to file
    df_rep.to_csv(squats_rep_summary_path, sep=sep_rep_summary, index=False)
    print(f"Successfully saved updated rep summary to {squats_rep_summary_path}")

    # Append documentation section to phase4g_rep_segmentation_summary.txt
    doc_text = """
## Post-Phase-4G visual audit correction

Following visual review of the rep-segmentation overlay plots, four subjects originally classified as multi_rep were reclassified to single_rep:

- Subject 1682 (originally multi_rep, 2 reps): rep markers placed in pose-extraction gap regions rather than at true local minima
- Subject 1774 (originally multi_rep, 3 reps): rep markers placed along a noisy single descent, no distinct rep bottoms identifiable
- Subject 1823 (originally multi_rep, 2 reps): first rep marker placed in a pose-extraction gap, no real second rep visible
- Subject 1884 (originally multi_rep, 2 reps): first rep marker placed mid-descent, not at a true local minimum

Methodological observation: the rep-detection algorithm (scipy.signal.find_peaks with prominence=20, distance=15) appears unsuited to fragmented in-the-wild YouTube cohort data. The algorithm is retained in the pipeline for future application to controlled multi-rep datasets (e.g., MM-Fit) where rep structure is cleanly defined by recording protocol.

After correction, all 10 included subjects are classified as single_rep. Within-subject repeatability (CV) biomarkers are not computed for the YouTube cohort. These biomarkers will be computed for future controlled-recording cohorts where multi-rep structure is verified.
"""

    # Read current content to ensure we handle newlines nicely
    with open(phase4g_summary_path, 'r', encoding='utf-8') as f:
        current_content = f.read()

    # Make sure we have clear spacing before appending
    if not current_content.endswith('\n'):
        spacing = '\n\n'
    elif current_content.endswith('\n\n'):
        spacing = ''
    else:
        spacing = '\n'

    with open(phase4g_summary_path, 'a', encoding='utf-8') as f:
        f.write(spacing + doc_text.strip() + '\n')

    print(f"Successfully appended documentation to {phase4g_summary_path}")

if __name__ == "__main__":
    main()
