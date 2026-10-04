import json
import zipfile
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MORPHEME_DIR = BASE_DIR / "crow_morpheme"

video_zips = list(BASE_DIR.rglob("01_crowd_video.zip"))

if not video_zips:
    raise FileNotFoundError("01_crowd_video.zip을 찾지 못했습니다.")

VIDEO_ZIP = video_zips[0]


# --------------------------------------------------
# 1. JSON에서 '있어야 하는 영상 파일명' 추출
# --------------------------------------------------

expected_videos = set()

for json_path in MORPHEME_DIR.rglob("*.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        video_name = obj.get("metaData", {}).get("name", "")

        if video_name:
            expected_videos.add(Path(video_name).name)

    except Exception as e:
        print("[JSON ERROR]", json_path, e)


# --------------------------------------------------
# 2. ZIP 안에 실제로 들어 있는 MP4 파일명 추출
# --------------------------------------------------

actual_videos = set()

with zipfile.ZipFile(VIDEO_ZIP, "r") as zf:
    for info in zf.infolist():

        filename = Path(info.filename).name

        if filename.lower().endswith(".mp4"):
            actual_videos.add(filename)


# --------------------------------------------------
# 3. 비교
# --------------------------------------------------

missing = sorted(expected_videos - actual_videos)
extra = sorted(actual_videos - expected_videos)

matched = expected_videos & actual_videos


print("===== 기본 통계 =====")
print("JSON이 가리키는 고유 영상 수:", len(expected_videos))
print("ZIP 안 실제 MP4 수:", len(actual_videos))
print("정확히 매칭된 영상 수:", len(matched))
print("JSON에는 있지만 ZIP에는 없는 영상:", len(missing))
print("ZIP에는 있지만 JSON에는 없는 영상:", len(extra))


# --------------------------------------------------
# 4. 누락 파일 제공자별 통계
# --------------------------------------------------

missing_signers = Counter()

for name in missing:
    if "_CROWD" in name:
        try:
            signer = name.split("_CROWD")[1].split("_")[0]
            missing_signers[signer] += 1
        except Exception:
            pass


print()
print("===== 누락 영상 제공자별 =====")

for signer, count in sorted(missing_signers.items()):
    print(f"CROWD{signer}: {count}")


# --------------------------------------------------
# 5. 지숫자 범위만 별도 확인
# --------------------------------------------------

numeric_expected = {
    name
    for name in expected_videos
    if any(
        f"FS{n:04d}" in name
        for n in range(801, 1001)
    )
}

numeric_actual = numeric_expected & actual_videos
numeric_missing = sorted(numeric_expected - actual_videos)


print()
print("===== 지숫자 FS0801~FS1000 =====")
print("JSON 기준 예상 영상 수:", len(numeric_expected))
print("ZIP에 실제 존재:", len(numeric_actual))
print("누락:", len(numeric_missing))


print()
print("===== 누락 지숫자 영상 처음 50개 =====")

for name in numeric_missing[:50]:
    print(name)


print()
print("===== JSON에 없는 ZIP 영상 처음 50개 =====")

for name in extra[:50]:
    print(name)