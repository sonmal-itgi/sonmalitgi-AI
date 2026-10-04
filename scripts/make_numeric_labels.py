import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "fs_labels.csv"
OUTPUT_FILE = BASE_DIR / "numeric_labels.csv"

rows = []

with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        fs_id = row["fs_id"]

        number = int(fs_id.replace("FS", ""))

        if 801 <= number <= 1000:
            rows.append(row)

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["fs_id", "label"]
    )

    writer.writeheader()
    writer.writerows(rows)

print("지숫자 표현 수:", len(rows))
print("저장 위치:", OUTPUT_FILE)

for row in rows[:20]:
    print(row["fs_id"], "->", row["label"])