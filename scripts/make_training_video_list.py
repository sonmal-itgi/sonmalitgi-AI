import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MANIFEST = BASE_DIR / "numeric_1to12" / "manifest.csv"
OUTPUT = BASE_DIR / "numeric_1to12" / "training_video_names.txt"

names = []

with open(MANIFEST, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["split"] == "Training":
            names.append(row["video_name"])

names = sorted(set(names))

with open(OUTPUT, "w", encoding="utf-8") as f:
    for name in names:
        f.write(name + "\n")

print("Training 영상 이름 수:", len(names))
print("저장 위치:", OUTPUT)

print()
print("===== 처음 20개 =====")
for name in names[:20]:
    print(name)