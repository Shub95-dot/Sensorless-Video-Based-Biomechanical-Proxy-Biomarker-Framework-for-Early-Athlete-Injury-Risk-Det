# Pose Quality Stratification Methods Note

Pose quality was stratified into three analysis tiers. Gold Tier frames contained complete bilateral hip-knee-ankle chains and were considered suitable for bilateral lower-body biomechanical analysis. Unilateral Tier frames contained at least one complete hip-knee-ankle chain and were considered suitable for visible-side single-limb analysis. Rejected Tier frames lacked a complete unilateral lower-body chain or had no pose detection and were excluded from Phase 4 biomechanical feature extraction.

## Caveat
MediaPipe's `visibility` attribute is a model-internal confidence score, not a ground-truth measure of anatomical landmark accuracy. Therefore, high visibility does not guarantee perfect landmark localisation.
