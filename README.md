# smart-farm-project
수경재배 환경 제어 및 모니터링 시스템


1. 프로젝트 소개
IoT 기반 스마트팜 기술을 활용하여, 수경재배 환경을 실시간으로 모니터링하고 제어하는 시스템입니다.
STM32, ESP32, Raspberry Pi 등의 장치를 연동하여 센서 데이터 수집부터 데이터베이스 저장, 웹 기반 모니터링 및 장치 제어 기능을 구현했습니다. 또한 ESP32-CAM과 OpenCV, YOLO를 활용한 영상 인식 기술을 적용하여 빨간 과일 탐지 및 불꽃 감지 기능을 구현했습니다.

2. 주요 기능
- 센서 데이터를 수집하고 데이터베이스에 저장
- 웹 대시보드를 통한 재배 환경 모니터링
- 센서 데이터에 따른 재배 환경 제어
- ESP32-CAM 영상 스트리밍 연동
- OpenCV 및 YOLO 기반 빨간 과일 탐지 및 불꽃 감지

3. 개발 환경
- MCU 및 장치 : STM32 (STM32F446RE), ESP32, ESP32-CAM, Raspberry Pi 4
- 프로그래밍 언어 : C (HAL 라이브러리), Python
- 개발 도구 : STM32CubeIDE, Visual Studio Code
- 서버 및 데이터베이스 : Flask, MariaDB
- 영상 처리 및 인식 : OpenCV, YOLO

4. 담당역할
- STM32와 ESP32 간 UART 시리얼 통신 구현
- ESP32와 Flask 서버 간 WebSocket 통신 구현
- ESP32-CAM과 Flask 서버 간 영상 스트리밍 연동
- OpenCV 및 YOLO 기반 영상 처리 및 객체 인식 기능 구현
- 수온 센서 데이터 수집 기능 구현
- 소스 코드 통합 및 시스템 연동 테스트
