## Subject inclusion criteria — Phase 4D

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

**Effective sample size for biomarker analysis: n = 11** (8 gold + 3 bronze), with 3 documented exclusions.

**Limitation:** the 70% validity threshold is a methodological choice consistent with published markerless-biomechanics inclusion criteria (typical range 60%–85%), but is not derived from this dataset. It is a fixed a priori cutoff.

## Post-Phase-4F audit update

Following Phase 4F biomarker extraction and visual review of the per-subject biomarker overlay plots, one additional subject was reclassified:

- Subject 1708: reclassified from `bronze` to `excluded`. The smoothed trajectory was heavily fragmented and visual inspection confirmed no coherent single-rep structure within the captured frames. The biomarker values computed in Phase 4F for this subject remain in the output CSV as records of the pipeline's behaviour but are excluded from all downstream analysis via the updated inclusion_tier.

Updated effective sample size: 10 subjects (8 gold + 2 bronze), with 5 documented exclusions (1683, 1708, 1709, 1789, 1869).
