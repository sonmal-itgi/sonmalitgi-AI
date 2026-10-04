import re
import zipfile
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

video_zips = list(BASE_DIR.rglob("01_crowd_video.zip"))

if not video_zips:
    raise FileNotFoundError("01_crowd_video.zip을 찾지 못했습니다.")

VIDEO_ZIP = video_zips[0]

OUTPUT_DIR = BASE_DIR / "numeric_validation" / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# _F.mp4 와 _F_.mp4 모두 허용
pattern = re.compile(
    r"NIA_SL_FS(\d+)_CROWD(\d+)_F_?\.mp4$",
    re.IGNORECASE
)


selected = {}
duplicate_keys = []


print("영상 ZIP:")
print(VIDEO_ZIP)
print()


with zipfile.ZipFile(VIDEO_ZIP, "r") as zf:

    # -----------------------------------
    # 지숫자 영상 탐색
    # -----------------------------------

    for info in zf.infolist():

        original_name = Path(info.filename).name

        match = pattern.match(original_name)

        if not match:
            continue

        fs_number = int(match.group(1))
        signer = int(match.group(2))

        # 지숫자만 사용
        if not 801 <= fs_number <= 1000:
            continue

        key = (fs_number, signer)

        if key in selected:
            duplicate_keys.append(key)
        else:
            selected[key] = info


    print("고유 지숫자 영상 수:", len(selected))
    print("중복 FS/제공자 조합:", len(duplicate_keys))


    # -----------------------------------
    # 제공자별 확인
    # -----------------------------------

    signer_counts = Counter(
        signer
        for _, signer in selected.keys()
    )

    print()
    print("===== 제공자별 영상 수 =====")

    for signer, count in sorted(signer_counts.items()):
        print(f"CROWD{signer:02d}: {count}")


    # -----------------------------------
    # 클래스 수 확인
    # -----------------------------------

    fs_ids = {
        fs_number
        for fs_number, _ in selected.keys()
    }

    print()
    print("고유 지숫자 클래스 수:", len(fs_ids))


    missing_fs = sorted(
        set(range(801, 1001)) - fs_ids
    )

    print("영상이 전혀 없는 FS 수:", len(missing_fs))

    if missing_fs:
        print(
            ", ".join(
                f"FS{x:04d}"
                for x in missing_fs
            )
        )


    # -----------------------------------
    # 영상 추출
    # -----------------------------------

    print()
    print("===== 영상 추출 =====")

    total = len(selected)

    for index, ((fs_number, signer), info) in enumerate(
        sorted(selected.items()),
        start=1
    ):

        # 원본 파일명이 _F_.mp4여도
        # 출력 파일명은 _F.mp4로 통일
        canonical_name = (
            f"NIA_SL_FS{fs_number:04d}"
            f"_CROWD{signer:02d}_F.mp4"
        )

        output_path = OUTPUT_DIR / canonical_name

        if not output_path.exists():

            with zf.open(info) as src:
                with open(output_path, "wb") as dst:

                    while True:

                        chunk = src.read(1024 * 1024)

                        if not chunk:
                            break

                        dst.write(chunk)

        if index % 20 == 0 or index == total:
            print(
                f"[{index}/{total}] "
                f"{canonical_name}"
            )


print()
print("===== 완료 =====")

saved_files = list(
    OUTPUT_DIR.glob("*.mp4")
)

print("저장 위치:", OUTPUT_DIR)
print("실제 저장된 MP4 수:", len(saved_files))