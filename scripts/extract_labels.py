import csv
import json
import re
from pathlib import Path


# 현재 이 Python 파일이 있는 aiHub 폴더
BASE_DIR = Path(__file__).resolve().parent

# 압축 해제했던 morpheme JSON 폴더
MORPHEME_DIR = BASE_DIR / "crow_morpheme"

# 결과 파일
MANIFEST_PATH = BASE_DIR / "validation_manifest.csv"
LABELS_PATH = BASE_DIR / "fs_labels.csv"


def fs_sort_key(fs_id):
    """FS0493 -> 493 형태로 정렬하기 위한 함수"""
    try:
        return int(fs_id.replace("FS", ""))
    except ValueError:
        return 999999


all_rows = []
unique_labels = {}
label_conflicts = []

json_files = list(MORPHEME_DIR.rglob("*.json"))

print(f"찾은 JSON 파일 수: {len(json_files)}")


for json_path in json_files:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        metadata = obj.get("metaData", {})
        video_name = metadata.get("name", "")
        duration = metadata.get("duration", "")

        # 예:
        # NIA_SL_FS0493_CROWD18_F.mp4
        match = re.search(
            r"(FS\d+)_CROWD(\d+)_F",
            video_name
        )

        if not match:
            print(f"[파일명 분석 실패] {video_name}")
            continue

        fs_id = match.group(1)
        signer = f"CROWD{match.group(2)}"

        data_list = obj.get("data", [])

        labels = []
        starts = []
        ends = []

        for segment in data_list:
            starts.append(segment.get("start", ""))
            ends.append(segment.get("end", ""))

            for attr in segment.get("attributes", []):
                name = attr.get("name", "")
                if name:
                    labels.append(name)

        # 중복 제거하면서 순서 유지
        labels = list(dict.fromkeys(labels))

        label = " / ".join(labels)

        start = starts[0] if starts else ""
        end = ends[-1] if ends else ""

        row = {
            "fs_id": fs_id,
            "label": label,
            "signer": signer,
            "video_name": video_name,
            "duration": duration,
            "start": start,
            "end": end,
            "json_path": str(json_path),
        }

        all_rows.append(row)

        # FS ID별 대표 label 저장
        if fs_id not in unique_labels:
            unique_labels[fs_id] = label
        elif unique_labels[fs_id] != label:
            label_conflicts.append(
                (
                    fs_id,
                    unique_labels[fs_id],
                    label
                )
            )

    except Exception as e:
        print(f"[ERROR] {json_path}")
        print(e)


# 모든 Validation 샘플 정보 저장
all_rows.sort(
    key=lambda x: (
        fs_sort_key(x["fs_id"]),
        x["signer"]
    )
)

with open(
    MANIFEST_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "fs_id",
            "label",
            "signer",
            "video_name",
            "duration",
            "start",
            "end",
            "json_path",
        ],
    )

    writer.writeheader()
    writer.writerows(all_rows)


# FS ID별 고유 표현 목록 저장
with open(
    LABELS_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    writer = csv.writer(f)

    writer.writerow(
        [
            "fs_id",
            "label"
        ]
    )

    for fs_id in sorted(
        unique_labels,
        key=fs_sort_key
    ):
        writer.writerow(
            [
                fs_id,
                unique_labels[fs_id]
            ]
        )


print()
print("===== 완료 =====")
print(f"전체 샘플 수: {len(all_rows)}")
print(f"고유 FS 표현 수: {len(unique_labels)}")
print(f"라벨 불일치 수: {len(label_conflicts)}")
print()
print(f"전체 Manifest: {MANIFEST_PATH}")
print(f"고유 Label 목록: {LABELS_PATH}")

print()
print("===== 처음 20개 표현 =====")

for fs_id in sorted(
    unique_labels,
    key=fs_sort_key
)[:20]:
    print(
        f"{fs_id} -> {unique_labels[fs_id]}"
    )


if label_conflicts:
    print()
    print("===== 서로 다른 label이 발견된 FS =====")

    for conflict in label_conflicts[:20]:
        print(conflict)