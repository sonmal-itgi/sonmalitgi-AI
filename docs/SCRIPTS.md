# Python Scripts

손말잇기 AI 개발 과정에서 사용한 데이터 분석, 전처리 및 모델 학습 스크립트입니다.

## AI Hub 데이터 분석

| 파일 | 역할 |
|---|---|
| `extract_labels.py` | CROWD morpheme JSON에서 FS ID와 라벨을 추출하고 `fs_labels.csv`, validation manifest를 생성 |
| `make_numeric_labels.py` | FS0801~FS1000 범위의 지숫자 200개 라벨 목록 생성 |
| `inspect_video_zip.py` | CROWD 영상 ZIP 내부의 제공자, FS 클래스, 영상 개수 등을 검사 |
| `compare_json_video.py` | JSON의 `metaData.name`과 실제 ZIP 영상 파일명을 비교해 파일명 불일치 검사 |
| `extract_numeric_videos.py` | Validation CROWD ZIP에서 지숫자 FS0801~FS1000 영상만 선택 추출 |
| `analyze_all_labels.py` | Training/Validation의 전체 morpheme JSON을 분석해 클래스, 제공자, 촬영각도, annotation 통계를 생성 |
| `make_class_catalog.py` | FS 1,000개, WORD 3,000개, SEN 2,000개의 사람이 보기 쉬운 클래스 목록 생성 |

## 1~12 Baseline 데이터 구성

| 파일 | 역할 |
|---|---|
| `make_1to12_manifest.py` | FS0801~FS0812(숫자 1~12)만 선택해 학습용 manifest 생성 |
| `make_training_video_list.py` | 1~12 Training 영상 파일명 목록 생성 |
| `extract_1to12_training.py` | `06_crowd_video.zip`에서 CROWD16, CROWD17의 1~12 영상을 추출 |
| `extract_1to12_training_01.py` | `01_crowd_video.zip`에서 CROWD01~03의 1~12 영상을 추가 추출 |
| `prepare_1to12_baseline.py` | baseline v1용 Training/Validation 데이터와 manifest 구성 |
| `prepare_1to12_baseline_v2.py` | Training 제공자를 5명으로 확장한 baseline v2 manifest 구성 |

## MediaPipe 전처리

| 파일 | 역할 |
|---|---|
| `test_mediapipe_one_video.py` | 영상 한 개에 MediaPipe Hands를 적용해 손 landmark 검출 여부를 시각적으로 확인 |
| `extract_landmarks_1to12.py` | baseline v1 영상에서 양손 landmark를 추출하여 `.npy` 시퀀스로 저장 |
| `extract_landmarks_1to12_v2.py` | baseline v2의 84개 영상에 동일한 landmark 전처리를 적용 |

한 프레임의 feature는 다음과 같이 구성됩니다.

```text
왼손 21 landmarks × (x, y, z)  = 63
오른손 21 landmarks × (x, y, z) = 63
왼손/오른손 존재 여부            = 2

총 128 features / frame