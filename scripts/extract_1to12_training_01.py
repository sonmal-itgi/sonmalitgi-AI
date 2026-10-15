import re
import zipfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

ZIP_PATH = (
    BASE_DIR
    / "004.수어영상"
    / "1.Training"
    / "원천데이터"
    / "CROWD"
    / "01_crowd_video.zip"
)

OUTPUT_DIR = (
    BASE_DIR
    / "numeric_1to12"
    / "training"
    / "videos"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


pattern = re.compile(
    r"NIA_SL_FS(\d+)_CROWD(\d+)_F_?\.mp4$",
    re.IGNORECASE,
)


selected = []


with zipfile.ZipFile(ZIP_PATH, "r") as zf:

    for info in zf.infolist():

        filename = Path(info.filename).name

        match = pattern.match(filename)

        if not match:
            continue

        fs_number = int(
            match.group(1)
        )

        signer = int(
            match.group(2)
        )

        if 801 <= fs_number <= 812:

            selected.append(
                (
                    info,
                    fs_number,
                    signer,
                )
            )


    print(
        "선택된 영상 수:",
        len(selected)
    )


    for index, (
        info,
        fs_number,
        signer,
    ) in enumerate(
        sorted(
            selected,
            key=lambda x: (
                x[1],
                x[2],
            ),
        ),
        start=1,
    ):

        output_name = (
            f"NIA_SL_FS{fs_number:04d}"
            f"_CROWD{signer:02d}_F.mp4"
        )

        output_path = (
            OUTPUT_DIR
            / output_name
        )

        if not output_path.exists():

            with zf.open(info) as src:
                with open(
                    output_path,
                    "wb"
                ) as dst:

                    while True:

                        chunk = src.read(
                            1024 * 1024
                        )

                        if not chunk:
                            break

                        dst.write(chunk)

        print(
            f"[{index}/{len(selected)}] "
            f"{output_name}"
        )


print()
print("===== 완료 =====")

saved = list(
    OUTPUT_DIR.glob("*.mp4")
)

print(
    "Training 폴더 전체 영상 수:",
    len(saved)
)