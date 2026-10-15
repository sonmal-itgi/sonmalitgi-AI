import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "label_analysis" / "all_samples.csv"
OUTPUT_DIR = BASE_DIR / "numeric_1to12"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "manifest.csv"

TARGET_IDS = {
    f"FS{i:04d}"
    for i in range(801, 813)
}

LABELS = {
    f"FS{i:04d}": str(i - 800)
    for i in range(801, 813)
}

selected = []

with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:

        if row["type"] != "FS":
            continue

        if row["class_id"] not in TARGET_IDS:
            continue

        selected.append({
            "split": row["split"],
            "class_id": row["class_id"],
            "label": LABELS[row["class_id"]],
            "signer": row["signer"],
            "angle": row["angle"],
            "video_name": row["video_name"],
            "duration": row["duration"],
            "start": row["start"],
            "end": row["end"],
            "json_path": row["json_path"],
        })


selected.sort(
    key=lambda x: (
        x["split"],
        int(x["class_id"].replace("FS", "")),
        x["signer"],
    )
)


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "split",
            "class_id",
            "label",
            "signer",
            "angle",
            "video_name",
            "duration",
            "start",
            "end",
            "json_path",
        ],
    )

    writer.writeheader()
    writer.writerows(selected)


training = [
    row for row in selected
    if row["split"] == "Training"
]

validation = [
    row for row in selected
    if row["split"] == "Validation"
]


print("===== 1~12 데이터 Manifest =====")
print("전체:", len(selected))
print("Training:", len(training))
print("Validation:", len(validation))

print()
print("===== 클래스별 개수 =====")

for fs_num in range(801, 813):

    fs_id = f"FS{fs_num:04d}"

    train_count = sum(
        1
        for row in training
        if row["class_id"] == fs_id
    )

    val_count = sum(
        1
        for row in validation
        if row["class_id"] == fs_id
    )

    print(
        f"{fs_id} ({LABELS[fs_id]:>2}) "
        f"Training={train_count:2d}, "
        f"Validation={val_count:2d}"
    )

print()
print("저장 위치:")
print(OUTPUT_FILE)