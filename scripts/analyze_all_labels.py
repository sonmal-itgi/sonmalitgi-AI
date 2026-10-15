import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "all_morpheme"

OUTPUT_DIR = BASE_DIR / "label_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALL_SAMPLES_CSV = OUTPUT_DIR / "all_samples.csv"
CLASS_SUMMARY_CSV = OUTPUT_DIR / "class_summary.csv"
CLASS_VARIANTS_CSV = OUTPUT_DIR / "class_variants.csv"
LABEL_CONFLICTS_CSV = OUTPUT_DIR / "label_conflicts.csv"
OVERVIEW_CSV = OUTPUT_DIR / "dataset_overview.csv"


# ---------------------------------------------------------
# 분석할 데이터 위치
# ---------------------------------------------------------

DATASETS = [
    {
        "split": "Training",
        "type": "FS",
        "source": "CROWD",
        "path": DATA_DIR / "training" / "crowd",
    },
    {
        "split": "Training",
        "type": "WORD",
        "source": "REAL",
        "path": DATA_DIR / "training" / "word",
    },
    {
        "split": "Training",
        "type": "SEN",
        "source": "REAL",
        "path": DATA_DIR / "training" / "sentence",
    },
    {
        "split": "Validation",
        "type": "FS",
        "source": "CROWD",
        "path": DATA_DIR / "validation" / "crowd",
    },
    {
        "split": "Validation",
        "type": "WORD",
        "source": "REAL",
        "path": DATA_DIR / "validation" / "word",
    },
    {
        "split": "Validation",
        "type": "SEN",
        "source": "REAL",
        "path": DATA_DIR / "validation" / "sentence",
    },
]


# ---------------------------------------------------------
# 통계 저장용
# ---------------------------------------------------------

class_stats = {}
overview = defaultdict(
    lambda: {
        "samples": 0,
        "classes": set(),
        "signers": set(),
        "angles": set(),
    }
)

error_count = 0
processed_count = 0


# ---------------------------------------------------------
# 파일명 분석
#
# 예:
# NIA_SL_FS0307_CROWD05_F.mp4
# NIA_SL_WORD0001_REAL05_D.mp4
# NIA_SL_SEN0799_REAL05_D.mp4
#
# 일부 _F_.mp4 같은 파일명도 허용
# ---------------------------------------------------------

filename_pattern = re.compile(
    r"NIA_SL_"
    r"(FS\d+|WORD\d+|SEN\d+)"
    r"_"
    r"(CROWD|REAL)"
    r"(\d+)"
    r"(?:_U)?"
    r"_"
    r"([FUDRL])"
    r"_?"
    r"\.mp4$",
    re.IGNORECASE,
)


def extract_annotation(data_list):
    """
    JSON의 data 배열에서 형태소/라벨을 순서대로 추출한다.

    단어/지화:
        고민

    문장:
        지금 / 차내리다 / 맞다
    """

    segments = []

    for segment in data_list:
        names = []

        for attr in segment.get("attributes", []):
            name = attr.get("name", "")

            if name:
                names.append(str(name).strip())

        if names:
            # 같은 segment에 여러 attribute가 있으면 + 로 연결
            segments.append(" + ".join(names))

    return " / ".join(segments)


# ---------------------------------------------------------
# all_samples.csv 작성
# ---------------------------------------------------------

with open(
    ALL_SAMPLES_CSV,
    "w",
    newline="",
    encoding="utf-8-sig",
) as output_file:

    fieldnames = [
        "split",
        "type",
        "class_id",
        "source",
        "signer",
        "angle",
        "video_name",
        "duration",
        "segment_count",
        "annotation",
        "start",
        "end",
        "json_path",
    ]

    writer = csv.DictWriter(
        output_file,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    # -----------------------------------------------------
    # 데이터 종류별 순회
    # -----------------------------------------------------

    for dataset in DATASETS:

        split = dataset["split"]
        data_type = dataset["type"]
        source = dataset["source"]
        root = dataset["path"]

        json_files = list(root.rglob("*.json"))

        print()
        print("=" * 60)
        print(
            f"{split} / {data_type} "
            f"JSON 수: {len(json_files)}"
        )
        print("=" * 60)

        for json_path in json_files:

            try:
                with open(
                    json_path,
                    "r",
                    encoding="utf-8",
                ) as f:
                    obj = json.load(f)

                metadata = obj.get("metaData", {})

                video_name = str(
                    metadata.get("name", "")
                ).strip()

                duration = metadata.get(
                    "duration",
                    "",
                )

                data_list = obj.get("data", [])

                # -----------------------------------------
                # 파일명 분석
                # -----------------------------------------

                match = filename_pattern.match(video_name)

                if match:

                    class_id = match.group(1).upper()

                    detected_source = match.group(2).upper()

                    signer_number = match.group(3)

                    angle = match.group(4).upper()

                    signer = (
                        f"{detected_source}"
                        f"{int(signer_number):02d}"
                    )

                else:
                    # metaData.name 분석 실패 시
                    # JSON 파일명에서 ID만 최대한 찾음

                    id_match = re.search(
                        r"(FS\d+|WORD\d+|SEN\d+)",
                        json_path.name,
                        re.IGNORECASE,
                    )

                    class_id = (
                        id_match.group(1).upper()
                        if id_match
                        else ""
                    )

                    signer = ""
                    angle = ""

                # -----------------------------------------
                # annotation 생성
                # -----------------------------------------

                annotation = extract_annotation(
                    data_list
                )

                starts = [
                    segment.get("start")
                    for segment in data_list
                    if segment.get("start") is not None
                ]

                ends = [
                    segment.get("end")
                    for segment in data_list
                    if segment.get("end") is not None
                ]

                start = starts[0] if starts else ""
                end = ends[-1] if ends else ""

                # -----------------------------------------
                # CSV 작성
                # -----------------------------------------

                writer.writerow({
                    "split": split,
                    "type": data_type,
                    "class_id": class_id,
                    "source": source,
                    "signer": signer,
                    "angle": angle,
                    "video_name": video_name,
                    "duration": duration,
                    "segment_count": len(data_list),
                    "annotation": annotation,
                    "start": start,
                    "end": end,
                    "json_path": str(json_path),
                })

                # -----------------------------------------
                # class 통계
                # -----------------------------------------

                class_key = (
                    data_type,
                    class_id,
                )

                if class_key not in class_stats:

                    class_stats[class_key] = {
                        "total": 0,
                        "training": 0,
                        "validation": 0,
                        "signers": set(),
                        "angles": set(),
                        "annotations": Counter(),
                    }

                stat = class_stats[class_key]

                stat["total"] += 1

                if split == "Training":
                    stat["training"] += 1
                elif split == "Validation":
                    stat["validation"] += 1

                if signer:
                    stat["signers"].add(signer)

                if angle:
                    stat["angles"].add(angle)

                if annotation:
                    stat["annotations"][annotation] += 1

                # -----------------------------------------
                # overview
                # -----------------------------------------

                overview_key = (
                    split,
                    data_type,
                )

                overview[overview_key]["samples"] += 1
                overview[overview_key]["classes"].add(
                    class_id
                )

                if signer:
                    overview[overview_key]["signers"].add(
                        signer
                    )

                if angle:
                    overview[overview_key]["angles"].add(
                        angle
                    )

                processed_count += 1

                if processed_count % 50000 == 0:
                    print(
                        f"처리 완료: "
                        f"{processed_count:,} JSON"
                    )

            except Exception as e:

                error_count += 1

                print()
                print("[ERROR]")
                print(json_path)
                print(e)


# ---------------------------------------------------------
# class_summary.csv
# ---------------------------------------------------------

with open(
    CLASS_SUMMARY_CSV,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    fieldnames = [
        "type",
        "class_id",
        "total_samples",
        "training_samples",
        "validation_samples",
        "signer_count",
        "angle_count",
        "angles",
        "annotation_variant_count",
        "most_common_annotation",
        "most_common_annotation_count",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for (data_type, class_id), stat in sorted(
        class_stats.items(),
        key=lambda x: (
            x[0][0],
            x[0][1],
        ),
    ):

        annotations = stat["annotations"]

        if annotations:
            most_common_annotation, most_common_count = (
                annotations.most_common(1)[0]
            )
        else:
            most_common_annotation = ""
            most_common_count = 0

        writer.writerow({
            "type": data_type,
            "class_id": class_id,
            "total_samples": stat["total"],
            "training_samples": stat["training"],
            "validation_samples": stat["validation"],
            "signer_count": len(stat["signers"]),
            "angle_count": len(stat["angles"]),
            "angles": ",".join(
                sorted(stat["angles"])
            ),
            "annotation_variant_count": len(
                annotations
            ),
            "most_common_annotation":
                most_common_annotation,
            "most_common_annotation_count":
                most_common_count,
        })


# ---------------------------------------------------------
# class_variants.csv
#
# 같은 class ID에서 어떤 annotation들이 나왔는지
# 전부 기록
# ---------------------------------------------------------

with open(
    CLASS_VARIANTS_CSV,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "type",
        "class_id",
        "annotation",
        "count",
    ])

    for (data_type, class_id), stat in sorted(
        class_stats.items()
    ):

        for annotation, count in (
            stat["annotations"].most_common()
        ):

            writer.writerow([
                data_type,
                class_id,
                annotation,
                count,
            ])


# ---------------------------------------------------------
# label_conflicts.csv
#
# WORD / FS의 경우 한 클래스에서
# 여러 annotation이 나오는지 확인
#
# SENTENCE는 자연스럽게 여러 수어 표현이
# 존재할 수 있으므로 conflict 취급하지 않음
# ---------------------------------------------------------

with open(
    LABEL_CONFLICTS_CSV,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "type",
        "class_id",
        "variant_count",
        "annotations",
    ])

    for (data_type, class_id), stat in sorted(
        class_stats.items()
    ):

        annotations = stat["annotations"]

        if (
            data_type in {"FS", "WORD"}
            and len(annotations) > 1
        ):

            annotation_text = " | ".join(
                f"{name} ({count})"
                for name, count
                in annotations.most_common()
            )

            writer.writerow([
                data_type,
                class_id,
                len(annotations),
                annotation_text,
            ])


# ---------------------------------------------------------
# dataset_overview.csv
# ---------------------------------------------------------

with open(
    OVERVIEW_CSV,
    "w",
    newline="",
    encoding="utf-8-sig",
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "split",
        "type",
        "sample_count",
        "class_count",
        "signer_count",
        "angle_count",
        "angles",
    ])

    for (split, data_type), stat in sorted(
        overview.items()
    ):

        writer.writerow([
            split,
            data_type,
            stat["samples"],
            len(stat["classes"]),
            len(stat["signers"]),
            len(stat["angles"]),
            ",".join(
                sorted(stat["angles"])
            ),
        ])


# ---------------------------------------------------------
# 결과 출력
# ---------------------------------------------------------

print()
print("=" * 60)
print("분석 완료")
print("=" * 60)

print(f"처리한 JSON: {processed_count:,}")
print(f"오류: {error_count:,}")
print(f"고유 class ID: {len(class_stats):,}")

type_counts = Counter(
    data_type
    for data_type, _ in class_stats.keys()
)

print()
print("===== 클래스 수 =====")

for data_type, count in sorted(
    type_counts.items()
):
    print(
        f"{data_type}: {count:,}"
    )

print()
print("===== 생성된 CSV =====")
print(ALL_SAMPLES_CSV)
print(CLASS_SUMMARY_CSV)
print(CLASS_VARIANTS_CSV)
print(LABEL_CONFLICTS_CSV)
print(OVERVIEW_CSV)