# Phase 5C Format Notes
Date: 2026-06-18

## Item 1 — Bootstrap-method reconciliation
Verdict: MATCH: phase5c reuses phase5b's d and cluster-bootstrap implementation verbatim (reimplemented verbatim).

## Item 2 — Tier assignments
Tiers assigned to lunge biomarkers:
- **peak_flexion_deg**: d = 1.6904, CI = [0.8317, 3.4525], margin = 0.8317, tier = `reliable`
- **rom_deg**: d = -1.2653, CI = [-2.8682, -0.5852], margin = 0.5852, tier = `reliable`
- **mean_descent_velocity_deg_per_frame**: d = 1.1563, CI = [0.2863, 2.6316], margin = 0.2863, tier = `reliable`
- **peak_descent_velocity_deg_per_frame**: d = 1.1453, CI = [0.7512, 2.0354], margin = 0.7512, tier = `reliable`
- **jerk_proxy_std**: d = -1.0070, CI = [-1.3663, -0.6526], margin = 0.6526, tier = `reliable`
- **peak_ascent_velocity_deg_per_frame**: d = -0.9721, CI = [-1.6403, -0.6554], margin = 0.6554, tier = `reliable`
- **mean_ascent_velocity_deg_per_frame**: d = -0.7962, CI = [-2.0731, -0.0807], margin = 0.0807, tier = `reliable_marginal`
- **peak_extension_deg**: d = -0.4972, CI = [-1.7633, 0.1533], margin = 0.0000, tier = `not_reliable`
- **tempo_ratio**: d = -0.3796, CI = [-0.7240, 0.1386], margin = 0.0000, tier = `not_reliable`
