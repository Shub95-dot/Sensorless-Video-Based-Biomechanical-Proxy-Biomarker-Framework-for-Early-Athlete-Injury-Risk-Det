import os
import re

files_to_check = [
    "22_dissertation_writing/methods_v2.md",
    "22_dissertation_writing/results_dropjump_validation_v1.md",
    "22_dissertation_writing/results_squat_v1.md",
    "22_dissertation_writing/results_lunge_v1.md",
    "22_dissertation_writing/results_uncertainty_framework_v1.md",
    "22_dissertation_writing/results_baseline_v1.md",
    "22_dissertation_writing/results_digital_twin_v1.md",
    "22_dissertation_writing/results_screening_layer_v1.md",
    "22_dissertation_writing/results_xai_v1.md",
    "22_dissertation_writing/results_temporal_model_v1.md",
    "22_dissertation_writing/results_discussion_v1.md"
]

base_dir = r"c:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY"

pattern = re.compile(r'\b(chapter|ch\.)\s*(\d+)', re.IGNORECASE)

print(f"{'File':<40} | {'Main Header':<50} | {'References to Chapters'}")
print("-" * 120)

for rel_path in files_to_check:
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        print(f"File not found: {rel_path}")
        continue
    
    header = ""
    references = set()
    
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str.startswith("# "):
                header = line_str[2:]
            
            # Find references
            matches = pattern.findall(line_str)
            for m in matches:
                references.add(f"{m[0]} {m[1]}".title())
                
    # Format and print
    ref_str = ", ".join(sorted(references)) if references else "None"
    print(f"{rel_path:<40} | {header:<50} | {ref_str}")
