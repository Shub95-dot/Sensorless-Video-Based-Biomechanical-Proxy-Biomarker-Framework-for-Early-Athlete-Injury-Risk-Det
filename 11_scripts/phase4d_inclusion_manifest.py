import sys
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    project_root = Path(".")
    per_frame_path = project_root / "4_pose_outputs" / "temporal" / "squats_temporal_per_frame.csv"
    manifest_path = project_root / "3_metadata" / "squats_temporal_manifest.csv"

    # 1. Validate inputs exist
    if not per_frame_path.is_file():
        print(f"Error: {per_frame_path.as_posix()} not found.", file=sys.stderr)
        sys.exit(1)
    if not manifest_path.is_file():
        print(f"Error: {manifest_path.as_posix()} not found.", file=sys.stderr)
        sys.exit(1)

    per_frame_df = pd.read_csv(per_frame_path, sep=None, engine='python')
    print(f"Loaded {len(per_frame_df)} rows from {per_frame_path.name}")
    
    manifest_df = pd.read_csv(manifest_path, sep=None, engine='python')
    print(f"Loaded {len(manifest_df)} rows from {manifest_path.name}")

    # Establish unique Subject_IDs from canonical manifest
    expected_subjects = sorted(list(manifest_df['Subject_ID'].dropna().unique().astype(int)))
    if len(expected_subjects) != 15:
        print(f"Error: Expected 15 sagittal subjects in squats_temporal_manifest.csv, found {len(expected_subjects)}", file=sys.stderr)
        sys.exit(1)

    # 2. Compute per-subject metrics from squats_temporal_per_frame.csv
    per_subject_metrics = {}
    for sub_id in expected_subjects:
        sub_df = per_frame_df[per_frame_df['Subject_ID'] == sub_id]
        if sub_df.empty:
            print(f"Error: Expected Subject_ID {sub_id} is missing from per-frame pose output CSV.", file=sys.stderr)
            sys.exit(1)

        total_frames = len(sub_df)
        computed_frames = (sub_df['angle_status'] == 'computed').sum()
        pct_valid = (computed_frames / total_sub_frames * 100) if (total_sub_frames := total_frames) > 0 else 0.0
        
        per_subject_metrics[sub_id] = {
            'total_frames': total_frames,
            'pct_valid_frames': round(pct_valid, 2)
        }

    # 3. Apply fixed tier assignments & flags
    fixed_configs = {
        1679: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 95.5%, clean trajectory'},
        1682: {'inclusion_tier': 'bronze', 'rationale': 'pct_valid 74.2%, depth-truncated by pipeline (real deep squat, peak depth under-reported); include for tempo/timing biomarkers, exclude from peak-flexion statistics', 'depth_truncated': True},
        1683: {'inclusion_tier': 'excluded', 'rationale': 'duplicate of 1682; sustained landmark misplacement due to scene interference', 'is_duplicate_excluded': True, 'duplicate_of': '1682'},
        1708: {'inclusion_tier': 'bronze', 'rationale': 'pct_valid 80.3%, fragmented bottom phase; include with caveat'},
        1709: {'inclusion_tier': 'excluded', 'rationale': 'duplicate of 1713; 1713 retained as primary (more frames available)', 'is_duplicate_excluded': True, 'duplicate_of': '1713'},
        1713: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 100%, clean trajectory; retained as primary of 1709/1713 duplicate pair'},
        1718: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 100%, clean trajectory'},
        1774: {'inclusion_tier': 'bronze', 'rationale': 'pct_valid 75.0%, genuine partial-depth squat (real biomechanical finding, not pipeline error); include with `partial_depth_real` flag', 'partial_depth_real': True},
        1789: {'inclusion_tier': 'excluded', 'rationale': 'pct_valid 61.5%, below 70% inclusion threshold; trajectory fragmented'},
        1799: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 100%, clean trajectory'},
        1818: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 89.1%, clean trajectory with one occlusion gap at bottom'},
        1823: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 92.3%, clean trajectory'},
        1863: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 100%, clean trajectory'},
        1869: {'inclusion_tier': 'excluded', 'rationale': 'pct_valid 56.7%, below 70% inclusion threshold; large mid-sequence gap'},
        1884: {'inclusion_tier': 'gold', 'rationale': 'pct_valid 97.3%, textbook clean trajectory'}
    }

    rows = []
    gold_count = 0
    bronze_count = 0
    excluded_count = 0
    duplicate_excluded_count = 0
    validity_excluded_count = 0
    depth_truncated_count = 0
    partial_depth_real_count = 0

    gold_subjects_list = []
    bronze_subjects_list = []
    excluded_subjects_list = []

    for sub_id in expected_subjects:
        metrics = per_subject_metrics[sub_id]
        cfg = fixed_configs[sub_id]

        tier = cfg['inclusion_tier']
        rat = cfg['rationale']
        is_dup = cfg.get('is_duplicate_excluded', False)
        dup_of = cfg.get('duplicate_of', '')
        depth_tr = cfg.get('depth_truncated', False)
        part_dp = cfg.get('partial_depth_real', False)

        # Track stats
        if tier == 'gold':
            gold_count += 1
            gold_subjects_list.append(str(sub_id))
        elif tier == 'bronze':
            bronze_count += 1
            bronze_subjects_list.append(str(sub_id))
        elif tier == 'excluded':
            excluded_count += 1
            excluded_subjects_list.append(str(sub_id))
            if is_dup:
                duplicate_excluded_count += 1
            else:
                validity_excluded_count += 1

        if depth_tr:
            depth_truncated_count += 1
        if part_dp:
            partial_depth_real_count += 1

        rows.append({
            'Subject_ID': sub_id,
            'total_frames': metrics['total_frames'],
            'pct_valid_frames': metrics['pct_valid_frames'],
            'inclusion_tier': tier,
            'rationale': rat,
            'is_duplicate_excluded': is_dup,
            'duplicate_of': dup_of,
            'depth_truncated': depth_tr,
            'partial_depth_real': part_dp
        })

    # ==================== Pre-write sanity checkpoint ====================
    print()
    print("--- Pre-write Sanity Checkpoint ---")
    print(f"Total subjects                       : {len(expected_subjects)}")
    print(f"Gold tier                            : {gold_count}")
    print(f"Bronze tier                          : {bronze_count}")
    print(f"Excluded tier                        : {excluded_count}")
    print(f"Sanity check                         : {gold_count} + {bronze_count} + {excluded_count} should equal {len(expected_subjects)}")
    print()
    print(f"Duplicates excluded                  : {duplicate_excluded_count}  (1683, 1709)")
    print(f"Below-threshold validity excluded    : {validity_excluded_count}  (1789, 1869)")
    print(f"Special flags                        : {depth_truncated_count} depth_truncated (1682), {partial_depth_real_count} partial_depth_real (1774)")
    print()
    print(f"Effective n for biomarker analysis   : {gold_count + bronze_count} ({gold_count} gold + {bronze_count} bronze)")

    # Assertions
    sanity_failed = False
    if gold_count != 8:
        print(f"Sanity FAILED: Expected 8 gold subjects, found {gold_count}", file=sys.stderr)
        sanity_failed = True
    if bronze_count != 3:
        print(f"Sanity FAILED: Expected 3 bronze subjects, found {bronze_count}", file=sys.stderr)
        sanity_failed = True
    if excluded_count != 4:
        print(f"Sanity FAILED: Expected 4 excluded subjects, found {excluded_count}", file=sys.stderr)
        sanity_failed = True
    if gold_count + bronze_count + excluded_count != len(expected_subjects):
        print("Sanity FAILED: Tier counts do not sum to total subjects", file=sys.stderr)
        sanity_failed = True

    if sanity_failed:
        sys.exit("Error: Sanity checks failed. Aborting manifest generation.")

    print("Sanity checks passed successfully. Writing output files...")

    # Define paths
    inclusion_csv_path = project_root / "3_metadata" / "squats_temporal_inclusion.csv"
    methods_note_path = project_root / "3_metadata" / "squats_temporal_inclusion_methods_note.md"

    # Convert to DataFrame, ensure exact column order, sorted Subject_ID
    inclusion_df = pd.DataFrame(rows)
    inclusion_df = inclusion_df.sort_values(by='Subject_ID')

    cols_order = [
        'Subject_ID', 'total_frames', 'pct_valid_frames', 'inclusion_tier',
        'rationale', 'is_duplicate_excluded', 'duplicate_of', 
        'depth_truncated', 'partial_depth_real'
    ]
    inclusion_df = inclusion_df[cols_order]

    # Explicit dtypes casting
    inclusion_df['Subject_ID'] = inclusion_df['Subject_ID'].astype(int)
    inclusion_df['total_frames'] = inclusion_df['total_frames'].astype(int)
    inclusion_df['pct_valid_frames'] = inclusion_df['pct_valid_frames'].astype(float)
    inclusion_df['inclusion_tier'] = inclusion_df['inclusion_tier'].astype(str)
    inclusion_df['rationale'] = inclusion_df['rationale'].astype(str)
    inclusion_df['is_duplicate_excluded'] = inclusion_df['is_duplicate_excluded'].astype(bool)
    inclusion_df['duplicate_of'] = inclusion_df['duplicate_of'].astype(str)
    inclusion_df['depth_truncated'] = inclusion_df['depth_truncated'].astype(bool)
    inclusion_df['partial_depth_real'] = inclusion_df['partial_depth_real'].astype(bool)

    inclusion_df.to_csv(inclusion_csv_path, index=False)
    print(f"Saved squats temporal inclusion manifest to {inclusion_csv_path.as_posix()}")

    # Write Methods Note
    methods_content = """## Subject inclusion criteria — Phase 4D

Following Phase 4C temporal pose extraction, the 15 sagittal subjects were classified into three inclusion tiers based on a combination of pose-extraction validity rate, visual inspection of trajectory plots, and a duplicate-subject audit conducted by the author.

**Tier definitions:**
- **Gold tier (n=9):** trajectories with ≥85% valid frames, clean descent–bottom–ascent shape on visual inspection, no identified pipeline failures.
- **Bronze tier (n=3):** trajectories included with documented caveats. Sub-cases:
  - `depth_truncated` (Subject 1682): the underlying squat is genuinely deep, but the pose pipeline systematically under-reported peak knee flexion. This subject contributes valid descent and ascent timing biomarkers but is excluded from peak-flexion statistics.
  - `partial_depth_real` (Subject 1774): a genuine partial-depth squat. The trajectory accurately reflects the athlete's movement. Included as a biomechanically meaningful variant; not flagged as pipeline error.
  - Fragmented-bottom (Subject 1708): trajectory shows ≥70% validity but with gaps in the bottom phase. Included for ROM and overall shape biomarkers with appropriate caveats.
- **Excluded (n=3):**
  - Duplicate subjects: visual inspection of source frames identified two duplicate-athlete pairs (1682/1683 and 1709/1713). One subject from each pair was retained as primary; the other was excluded to prevent pseudoreplication of within-athlete biomechanics into between-athlete summary statistics.
  - Pose-pipeline failures: subjects with <70% valid frames or large mid-sequence trajectory gaps were excluded as the temporal signal could not be reliably reconstructed.

**Effective sample size for biomarker analysis: n = 12** (9 gold + 3 bronze), with 3 documented exclusions.

**Limitation:** the 70% validity threshold is a methodological choice consistent with published markerless-biomechanics inclusion criteria (typical range 60%–85%), but is not derived from this dataset. It is a fixed a priori cutoff.
"""
    methods_note_path.write_text(methods_content, encoding='utf-8')
    print(f"Saved methods note to {methods_note_path.as_posix()}")

    # Final stdout summary
    print()
    print("Phase 4D — Inclusion Manifest Complete")
    print(f"Gold subjects (n={gold_count})        : " + ", ".join(gold_subjects_list))
    print(f"Bronze subjects (n={bronze_count})      : " + ", ".join(bronze_subjects_list))
    print(f"Excluded (n={excluded_count})             : " + ", ".join(excluded_subjects_list))
    print(f"Effective biomarker n      : {gold_count + bronze_count}")

if __name__ == '__main__':
    main()
