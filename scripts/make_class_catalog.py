import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "label_analysis" / "class_summary.csv"
OUTPUT_DIR = BASE_DIR / "label_analysis" / "class_catalog"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

outputs = {
    "FS": OUTPUT_DIR / "fs_classes.csv",
    "WORD": OUTPUT_DIR / "word_classes.csv",
    "SEN": OUTPUT_DIR / "sentence_classes.csv",
}

writers = {}
files = {}

try:
    for data_type, path in outputs.items():
        f = open(path, "w", newline="", encoding="utf-8-sig")
        files[data_type] = f

        writer = csv.writer(f)
        writers[data_type] = writer

        if data_type == "FS":
            writer.writerow([
                "class_id",
                "category",
                "label",
                "annotation_variant_count",
                "training_samples",
                "validation_samples",
            ])

        elif data_type == "WORD":
            writer.writerow([
                "class_id",
                "label",
                "annotation_variant_count",
                "training_samples",
                "validation_samples",
            ])

        elif data_type == "SEN":
            writer.writerow([
                "class_id",
                "representative_expression",
                "annotation_variant_count",
                "training_samples",
                "validation_samples",
            ])

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data_type = row["type"]
            class_id = row["class_id"]

            if data_type == "FS":
                fs_number = int(class_id.replace("FS", ""))

                if 1 <= fs_number <= 800:
                    category = "지문자"
                elif 801 <= fs_number <= 1000:
                    category = "지숫자"
                else:
                    category = "기타"

                writers["FS"].writerow([
                    class_id,
                    category,
                    row["most_common_annotation"],
                    row["annotation_variant_count"],
                    row["training_samples"],
                    row["validation_samples"],
                ])

            elif data_type == "WORD":
                writers["WORD"].writerow([
                    class_id,
                    row["most_common_annotation"],
                    row["annotation_variant_count"],
                    row["training_samples"],
                    row["validation_samples"],
                ])

            elif data_type == "SEN":
                writers["SEN"].writerow([
                    class_id,
                    row["most_common_annotation"],
                    row["annotation_variant_count"],
                    row["training_samples"],
                    row["validation_samples"],
                ])

finally:
    for f in files.values():
        f.close()

print("===== 생성 완료 =====")

for data_type, path in outputs.items():
    print(data_type, "->", path)