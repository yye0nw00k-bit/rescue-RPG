# 태현이 구하기(?) / Rescue RPG

PC용 2D RPG와 Android용 터치 프로젝트입니다.

- `pc/`: Python/Tkinter PC 버전
- `android/`: Kivy Android 버전
- `.github/workflows/android.yml`: GitHub Actions에서 APK 빌드

## 현재 초기 업로드 단계
저장소 초기 설정 과정에서 `project_bundle.zip`을 자동으로 풀어 소스 파일을 배치하는 워크플로를 실행합니다. 워크플로가 끝나면 PC/Android 소스가 일반 파일로 보이게 됩니다.

## PC 실행
Windows에 Python 3와 Tkinter가 설치되어 있어야 합니다. `pc/실행하기.bat`을 실행하세요.

## Android APK
저장소의 **Actions** 탭에서 **Build Android APK**를 실행한 다음, 성공한 실행의 `taehyun-rescue-apk` 아티팩트를 다운로드하세요. APK는 아직 사전 컴파일된 파일이 아닙니다.

## 참고
계정과 저장 데이터는 로컬 기기에 저장됩니다. 기기 간 온라인 계정 동기화는 포함되지 않습니다.
