"""Quick script to update squat_quality_review.csv with quality labels."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "3_metadata" / "squat_quality_review.csv"

# Read
rows = []
with open(path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        row["Quality"] = "good"
        row["Selected"] = "yes"
        row["Notes"] = "Pre-cleaned dataset; accepted for initial pose extraction"
        rows.append(row)

# Write
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Verify
with open(path, "r", encoding="utf-8") as f:
    data = list(csv.DictReader(f))

total = len(data)
all_good = all(r["Quality"] == "good" for r in data)
all_yes = all(r["Selected"] == "yes" for r in data)
all_notes = all(r["Notes"] == "Pre-cleaned dataset; accepted for initial pose extraction" for r in data)
subs = len(set(r["Subject_ID"] for r in data))

print(f"Total selected rows : {total}")
print(f"All Quality = good  : {all_good}")
print(f"All Selected = yes  : {all_yes}")
print(f"All Notes filled    : {all_notes}")
print(f"Unique subjects     : {subs}")
print()
print("READY FOR PHASE 3" if all_good and all_yes and all_notes else "ISSUES FOUND")
