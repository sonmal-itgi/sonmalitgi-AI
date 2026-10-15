import csv
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# 기존 Validation 지숫자 400개
SOURCE_VALIDATION_DIR = (
    BASE_DIR
    / "numeric_validation"
    / "videos"
)

# 1~12 전용 폴더
DATASET_DIR = BASE_DIR / "numeric_1to12"

TRAIN_DIR = (
    DATASET_DIR
    / "training"
    / "videos"
)

VAL_DIR = (
    DATASET_DIR
    / "validation"
    / "videos"
)

VAL_DIR.mkdir(parents=True, exist_ok=True)


# 기존 전체 manifest
MANIFEST_FILE = (
    DATASET_DIR
    / "manifest.csv"
)

# 현재 실제로 사용할 작은 baseline manifest
BASELINE_MANIFEST = (
    DATASET_DIR
    / "baseline_manifest.csv"
)


# ------------------------------------------
# 1. Validation 영상 24개 복사
# ------------------------------------------

validation_signers = [
    "CROWD18",
    "CROWD19",
]

copied = 0

for fs_number in range(801, 813):

    fs_id = f"FS{fs_number:04d}"

    for signer in validation_signers:

        filename = (
            f"NIA_SL_{fs_id}_{signer}_F.mp4"
        )

        source = (
            SOURCE_VALIDATION_DIR
            / filename
        )

        destination = (
            VAL_DIR
            / filename
        )

        if not source.exists():
            print(
                "[없음]",
                source
            )
            continue

        if not destination.exists():
            shutil.copy2(
                source,
                destination
            )

        copied += 1


print(
    "Validation 준비 영상 수:",
    copied
)


# ------------------------------------------
# 2. 현재 실제 사용하는 signer만 선택
# ------------------------------------------

allowed = {
    "Training": {
        "CROWD16",
        "CROWD17",
    },
    "Validation": {
        "CROWD18",
        "CROWD19",
    },
}


rows = []
missing_videos = []


with open(
    MANIFEST_FILE,
    "r",
    encoding="utf-8-sig",
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        split = row["split"]
        signer = row["signer"]

        if split not in allowed:
            continue

        if signer not in allowed[split]:
            continue

        if split == "Training":
            video_path = (
                TRAIN_DIR
                / row["video_name"]
            )

        else:
            video_path = (
                VAL_DIR
                / row["video_name"]
            )

        if not video_path.exists():
            missing_videos.append(
                str(video_path)
            )

        new_row = dict(row)

        new_row["video_path"] = str(
            video_path
        )

        rows.append(new_row)


# ------------------------------------------
# 3. baseline_manifest.csv 저장
# ------------------------------------------

fieldnames = [
    "split",
    "class_id",
    "label",
    "signer",
    "angle",
    "video_name",
    "duration",
    "start",
    "end",
    "video_path",
    "json_path",
]


with open(
    BASELINE_MANIFEST,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(rows)


# ------------------------------------------
# 4. 결과 확인
# ------------------------------------------

training_rows = [
    r for r in rows
    if r["split"] == "Training"
]

validation_rows = [
    r for r in rows
    if r["split"] == "Validation"
]


print()
print("===== Baseline Dataset =====")

print(
    "Training:",
    len(training_rows)
)

print(
    "Validation:",
    len(validation_rows)
)

print(
    "전체:",
    len(rows)
)

print(
    "누락 영상:",
    len(missing_videos)
)

print()
print(
    "Manifest:",
    BASELINE_MANIFEST
)


if missing_videos:

    print()
    print("===== 누락 파일 =====")

    for path in missing_videos:
        print(path)