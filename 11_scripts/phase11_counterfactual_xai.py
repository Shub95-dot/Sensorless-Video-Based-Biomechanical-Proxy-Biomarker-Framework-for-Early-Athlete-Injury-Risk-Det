#!/usr/bin/env python3
"""
phase11_counterfactual_xai.py
=============================
Implements Step 11: Counterfactual XAI.
It loads the Step 10 screening outputs, generates mathematically faithful
counterfactual explanations, calculates the Minimal Kinematic Intervention (MKI)
under the coupling assumption, grades confidence against validated noise buffer limits,
and saves the structured explanations to 21_xai_outputs/worked_example_explanations.json.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENING_CSV = PROJECT_ROOT / "20_screening_outputs" / "worked_example_screening.csv"
OUT_DIR = PROJECT_ROOT / "21_xai_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Phase 7 Noise Floors
noise_floors = {
    "peak_flexion": 11.9885,    # deg
    "rom": 23.1666,             # deg
    "velocity": 40.8615         # deg/s
}

def generate_explanations(df):
    results = []
    
    for _, row in df.iterrows():
        # Only explain SCREENING_POSITIVE reps
        if row["screening_flag"] != "SCREENING_POSITIVE":
            continue
            
        rep_num = int(row["rep_number"])
        sub_id = int(row["subject_id"])
        video_id = row["video_id"]
        exercise = row["exercise"]
        
        fired_str = row["fired_rules"]
        fired_rules = fired_str.split(";") if fired_str != "None" else []
        
        explanations = []
        
        # Rule 1: EXCESS_DEPTH
        if "EXCESS_DEPTH" in fired_rules:
            margin = float(row["peak_flexion_margin"])
            val = float(row["peak_flexion_val"])
            thresh = float(row["peak_flexion_threshold"])
            
            # Confidence buffer is 0.5 * noise floor
            buffer_val = 0.5 * noise_floors["peak_flexion"]
            confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"
            
            text = (
                f"Flagged EXCESS_DEPTH because peak knee flexion joint angle ({val:.2f}°) was "
                f"{margin:.2f}° below the active baseline threshold ({thresh:.2f}°). "
                f"Had the peak flexion angle been at least {thresh:.2f}° (representing a shallower "
                f"bend of {margin:.2f}° less depth), the EXCESS_DEPTH flag would not have fired."
            )
            if confidence != "HIGH":
                text += (
                    f" Note: The deviation margin ({margin:.2f}°) is close to the monocular camera's "
                    f"validated measurement uncertainty boundaries. This flag should be interpreted "
                    f"with caution as minor tracking fluctuations could have triggered it."
                )
                
            explanations.append({
                "rule": "EXCESS_DEPTH",
                "margin": round(margin, 4),
                "confidence": confidence,
                "text": text
            })
            
        # Rule 2: EXCESS_VELOCITY
        if "EXCESS_VELOCITY" in fired_rules:
            margin = float(row["velocity_margin"])
            val = float(row["velocity_val"])
            thresh = float(row["velocity_threshold"])
            
            buffer_val = 0.5 * noise_floors["velocity"]
            confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"
            
            text = (
                f"Flagged EXCESS_VELOCITY because descent joint velocity ({val:.2f}°/s) was "
                f"{margin:.2f}°/s above the active baseline threshold ({thresh:.2f}°/s). "
                f"Had the descent velocity been no more than {thresh:.2f}°/s (representing a slower "
                f"movement of {margin:.2f}°/s less speed), the EXCESS_VELOCITY flag would not have fired."
            )
            if confidence != "HIGH":
                text += (
                    f" Note: The deviation margin ({margin:.2f}°/s) is close to the monocular camera's "
                    f"validated measurement uncertainty boundaries. This flag should be interpreted "
                    f"with caution as minor tracking fluctuations could have triggered it."
                )
                
            explanations.append({
                "rule": "EXCESS_VELOCITY",
                "margin": round(margin, 4),
                "confidence": confidence,
                "text": text
            })
            
        # Rule 3: EXCESS_ROM
        if "EXCESS_ROM" in fired_rules:
            margin = float(row["rom_margin"])
            val = float(row["rom_val"])
            thresh = float(row["rom_threshold"])
            
            buffer_val = 0.5 * noise_floors["rom"]
            confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"
            
            text = (
                f"Flagged EXCESS_ROM because knee range of motion ({val:.2f}°) was "
                f"{margin:.2f}° above the active baseline threshold ({thresh:.2f}°). "
                f"Had the range of motion been no more than {thresh:.2f}° (representing a restricted "
                f"excursion of {margin:.2f}° less joint travel), the EXCESS_ROM flag would not have fired."
            )
            if confidence != "HIGH":
                text += (
                    f" Note: The deviation margin ({margin:.2f}°) is close to the monocular camera's "
                    f"validated measurement uncertainty boundaries. This flag should be interpreted "
                    f"with caution as minor tracking fluctuations could have triggered it."
                )
                
            explanations.append({
                "rule": "EXCESS_ROM",
                "margin": round(margin, 4),
                "confidence": confidence,
                "text": text
            })
            
        # Compute Minimal Kinematic Intervention (MKI)
        mki_text = ""
        depth_margin = float(row["peak_flexion_margin"])
        rom_margin = float(row["rom_margin"])
        vel_margin = float(row["velocity_margin"])
        
        if "EXCESS_DEPTH" in fired_rules and "EXCESS_ROM" in fired_rules:
            mki_val = max(depth_margin, rom_margin)
            mki_text = (
                f"To clear all screening flags for this repetition, under the explicit assumption that range of motion "
                f"scales directly with peak flexion depth (assuming a constant standing extension start point), the subject "
                f"would need to reduce knee flexion depth (increase peak angle) by at least {mki_val:.2f}°, which would "
                f"simultaneously reduce active range of motion and clear both the EXCESS_DEPTH and EXCESS_ROM flags."
            )
            if "EXCESS_VELOCITY" in fired_rules:
                mki_text += f" Additionally, descent speed must be reduced by at least {vel_margin:.2f}°/s."
                
        elif "EXCESS_DEPTH" in fired_rules:
            mki_text = f"To clear the screening flag for this repetition, the subject would need to reduce knee flexion depth (increase peak angle) by at least {depth_margin:.2f}°."
            if "EXCESS_VELOCITY" in fired_rules:
                mki_text += f" Additionally, descent speed must be reduced by at least {vel_margin:.2f}°/s."
                
        elif "EXCESS_ROM" in fired_rules:
            mki_text = f"To clear the screening flag for this repetition, the subject would need to restrict knee range of motion by at least {rom_margin:.2f}°."
            if "EXCESS_VELOCITY" in fired_rules:
                mki_text += f" Additionally, descent speed must be reduced by at least {vel_margin:.2f}°/s."
                
        elif "EXCESS_VELOCITY" in fired_rules:
            mki_text = f"To clear the screening flag for this repetition, the subject would need to reduce descent joint velocity by at least {vel_margin:.2f}°/s."
            
        results.append({
            "subject_id": sub_id,
            "video_id": video_id,
            "exercise": exercise,
            "rep_number": rep_num,
            "screening_status": "SCREENING_POSITIVE",
            "fired_rules": fired_rules,
            "explanations": explanations,
            "minimal_kinematic_intervention": mki_text
        })
        
    return results

def main():
    print("=========================================================")
    print("RUNNING PHASE 11 COUNTERFACTUAL XAI EXPLANATIONS BUILD")
    print("=========================================================")
    
    if not SCREENING_CSV.is_file():
        print(f"Error: Step 10 screening CSV not found at: {SCREENING_CSV}")
        sys.exit(1)
        
    df_screening = pd.read_csv(SCREENING_CSV)
    
    # Generate explanations
    explanations_list = generate_explanations(df_screening)
    
    # Save JSON file
    out_json_path = OUT_DIR / "worked_example_explanations.json"
    with open(out_json_path, "w") as f:
        json.dump(explanations_list, f, indent=2)
    print(f"Saved counterfactual XAI explanations to: {out_json_path}")
    
    # Print out a sample of explanations for review (one squat rep and one lunge rep)
    print("\n--- SAMPLE XAI OUTPUT FOR SQUAT SUBJECT 8 (PM_113), REP 6 ---")
    sq_rep6 = [e for e in explanations_list if e["exercise"] == "Squat" and e["rep_number"] == 6]
    if sq_rep6:
        e = sq_rep6[0]
        print(f"Fired Rules: {e['fired_rules']}")
        print("Explanations:")
        for exp in e["explanations"]:
            print(f"  * [{exp['rule']}] (Confidence: {exp['confidence']})")
            print(f"    Text: {exp['text']}")
        print(f"MKI: {e['minimal_kinematic_intervention']}")
        
    print("\n--- SAMPLE XAI OUTPUT FOR LUNGE SUBJECT 6 (PM_104), REP 6 ---")
    lg_rep6 = [e for e in explanations_list if e["exercise"] == "Lunge" and e["rep_number"] == 6]
    if lg_rep6:
        e = lg_rep6[0]
        print(f"Fired Rules: {e['fired_rules']}")
        print("Explanations:")
        for exp in e["explanations"]:
            print(f"  * [{exp['rule']}] (Confidence: {exp['confidence']})")
            print(f"    Text: {exp['text']}")
        print(f"MKI: {e['minimal_kinematic_intervention']}")
        
    print("=========================================================")

if __name__ == "__main__":
    main()
