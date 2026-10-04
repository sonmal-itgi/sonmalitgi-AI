# 손말잇기 AI

손말잇기 서비스의 한국수어 인식 AI 개발 저장소

## 현재 목표

AI Hub 수어 영상 데이터를 활용하여 지숫자 인식 모델 구축

초기 AI 파이프라인:
MP4 -> MediaPipe -> Landmark Sequence -> LSTM -> 지숫자 분류

## 현재 진행 상황

- AI Hub 수어 영상 데이터 다운로드 및 구조 분석
- 지문자 / 지숫자 데이터 구분
- 지숫자 FS0801 ~ FS1000 확인
- Validation 지숫자 영상 400개 추출
- 데이터 파일명 불일치 처리
- Training 데이터 준비 예정

## 프로젝트 구조

```text
scripts/          데이터 분석 및 추출용 스크립트
src/
  preprocessing/ MediaPipe 전처리
  training/      모델 학습
  inference/     실시간 추론
docs/             개발 및 데이터 관련 문서