# Kinematic Screening Dashboard

Streamlit dashboard wrapping the sensorless kinematic screening pipeline
for the MSc AI/Data Science dissertation viva demonstration.

## Installation

```bash
# From the repository root
pip install -r dashboard/requirements.txt
```

Ensure the MediaPipe Heavy model is present at:
```
12_models/pose_landmarker_heavy.task
```

## Running

```bash
cd dashboard
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`.

**Offline mode:** The dashboard runs entirely locally. No internet
connection is required after installation.

## Sample Videos for Testing

REHAB24-6 squat videos (correct and incorrect reps):
```
1_raw_datasets/Rehab 26 dataset/REHAB24-6 integration/Squats/PM_113-Camera18-30fps-transposed.mp4
1_raw_datasets/Rehab 26 dataset/REHAB24-6 integration/Squats/PM_008-Camera18-30fps-transposed.mp4
```

REHAB24-6 lunge videos:
```
1_raw_datasets/Rehab 26 dataset/REHAB24-6 integration/Lunges/
```

## Troubleshooting

### "MediaPipe model not found"
Ensure `12_models/pose_landmarker_heavy.task` exists. Download from:
https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task

### "No pose detected in any frame"
- Ensure the video shows a person with visible lower body
- Check video is not too dark or blurry
- The subject should be in frame for the entire clip

### "Video too short"
Upload at least a 1-second clip (30+ frames at 30fps).

### Streamlit not found
```bash
pip install streamlit
```

### Slow processing
- Processing time depends on video length and resolution
- A 5-10 second video at 30fps should process in under 60 seconds on Intel i7
- Shorter clips process faster

## Framework Discipline

This dashboard performs **screening**, not prediction. All UI text
respects this distinction. No predictive language is used anywhere.
