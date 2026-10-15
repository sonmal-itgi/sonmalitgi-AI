import csv
from pathlib import Path

import cv2
import mediapipe as mp


BASE_DIR = Path(__file__).resolve().parent

MANIFEST_PATH = (
    BASE_DIR
    / "numeric_1to12"
    / "baseline_manifest.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "numeric_1to12"
    / "mediapipe_test"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Training 영상 중 첫 번째 샘플 선택
# --------------------------------------------------

sample = None

with open(
    MANIFEST_PATH,
    "r",
    encoding="utf-8-sig"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        if row["split"] == "Training":
            sample = row
            break


if sample is None:
    raise RuntimeError("Training 샘플을 찾지 못했습니다.")


video_path = Path(sample["video_path"])

start_time = float(sample["start"])
end_time = float(sample["end"])

print("===== 테스트 영상 =====")
print("class_id:", sample["class_id"])
print("label:", sample["label"])
print("signer:", sample["signer"])
print("video:", video_path)
print("수어 구간:", start_time, "~", end_time)


if not video_path.exists():
    raise FileNotFoundError(video_path)


# --------------------------------------------------
# MediaPipe Hands
# --------------------------------------------------

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    raise RuntimeError(
        f"영상을 열 수 없습니다: {video_path}"
    )


fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print()
print("FPS:", fps)
print("해상도:", width, "x", height)


# start 위치로 이동
cap.set(
    cv2.CAP_PROP_POS_MSEC,
    start_time * 1000
)


output_path = (
    OUTPUT_DIR
    / f"{sample['class_id']}_{sample['signer']}_mediapipe.mp4"
)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    str(output_path),
    fourcc,
    fps,
    (width, height)
)


frame_count = 0
detected_frames = 0


with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
) as hands:

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        current_time = (
            cap.get(cv2.CAP_PROP_POS_MSEC)
            / 1000.0
        )

        if current_time > end_time:
            break

        frame_count += 1

        # OpenCV BGR → MediaPipe RGB
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(rgb)

        if results.multi_hand_landmarks:

            detected_frames += 1

            for hand_landmarks in (
                results.multi_hand_landmarks
            ):

                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

        # 화면 왼쪽 위에 정보 표시
        text = (
            f"{sample['class_id']} "
            f"label={sample['label']} "
            f"time={current_time:.2f}s"
        )

        cv2.putText(
            frame,
            text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        writer.write(frame)


cap.release()
writer.release()


print()
print("===== 결과 =====")
print("처리 프레임:", frame_count)
print("손 검출 프레임:", detected_frames)

if frame_count > 0:
    detection_rate = (
        detected_frames / frame_count * 100
    )

    print(
        f"손 검출률: {detection_rate:.1f}%"
    )

print("결과 영상:")
print(output_path)