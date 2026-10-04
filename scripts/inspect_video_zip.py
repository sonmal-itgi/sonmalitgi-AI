import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

video_zips = list(BASE_DIR.rglob("01_crowd_video.zip"))

if not video_zips:
    raise FileNotFoundError("01_crowd_video.zip을 찾지 못했습니다.")

VIDEO_ZIP = video_zips[0]

pattern = re.compile(
    r"NIA_SL_FS(\d+)_CROWD(\d+)_F\.(mp4|avi)$",
    re.IGNORECASE
)

all_videos = []
numeric_videos = []
by_signer = Counter()
numeric_by_signer = Counter()
fs_to_signers = defaultdict(set)

with zipfile.ZipFile(VIDEO_ZIP, "r") as zf:
    for info in zf.infolist():
        filename = Path(info.filename).name

        match = pattern.match(filename)

        if not match:
            continue

        fs_num = int(match.group(1))
        signer = int(match.group(2))
        ext = match.group(3).lower()

        all_videos.append((fs_num, signer, ext, filename))
        by_signer[signer] += 1
        fs_to_signers[fs_num].add(signer)

        if 801 <= fs_num <= 1000:
            numeric_videos.append(
                (fs_num, signer, ext, filename)
            )
            numeric_by_signer[signer] += 1


print("영상 ZIP:")
print(VIDEO_ZIP)

print()
print("===== 전체 =====")
print("인식된 전체 영상 수:", len(all_videos))

print()
print("===== 제공자별 전체 영상 수 =====")
for signer, count in sorted(by_signer.items()):
    print(f"CROWD{signer:02d}: {count}")

print()
print("===== 지숫자 =====")
print("FS0801~FS1000 영상 수:", len(numeric_videos))

print()
print("===== 제공자별 지숫자 영상 수 =====")
for signer, count in sorted(numeric_by_signer.items()):
    print(f"CROWD{signer:02d}: {count}")


expected = set(range(801, 1001))
present = set(fs_num for fs_num, _, _, _ in numeric_videos)

missing = sorted(expected - present)

print()
print("===== 지숫자 클래스 =====")
print("존재하는 고유 지숫자 FS 수:", len(present))
print("아예 없는 FS 수:", len(missing))

print()
print("없는 FS:")
print(
    ", ".join(f"FS{x:04d}" for x in missing)
)


print()
print("===== 각 FS별 영상 개수 =====")

count_by_fs = Counter(
    fs_num for fs_num, _, _, _ in numeric_videos
)

for fs_num in range(801, 1001):
    count = count_by_fs.get(fs_num, 0)

    if count != 2:
        print(
            f"FS{fs_num:04d}: "
            f"{count}개, "
            f"signers={sorted(fs_to_signers.get(fs_num, []))}"
        )


print()
print("===== 확장자 =====")

extensions = Counter(
    ext for _, _, ext, _ in all_videos
)

for ext, count in extensions.items():
    print(ext, count)