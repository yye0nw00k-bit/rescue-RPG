# 태현이 구하기(?)

PC와 Android를 같은 Pygame 게임 코드로 실행하는 2D 횡스크롤 RPG 프로젝트입니다. 13개 지역을 돌파하고 마지막 보스를 물리쳐 태현이를 구출하세요. 구출 이후에는 태현이 키우기 모드로 전환됩니다.

## 플랫폼

- Windows PC: Pygame 기반 실행 파일을 사용합니다.
- Android: Buildozer와 python-for-android의 SDL2 bootstrap을 통해 APK를 빌드하도록 구성되어 있습니다. Pygame Android 빌드는 도구 체인 호환성의 영향을 받으므로, 빌드 성공 및 실제 기기 실행을 별도로 확인해야 합니다.
- 온라인 계정 서버: PC와 Android 모두 같은 온라인 API를 사용하도록 구성했습니다. 온라인 로그인과 저장에는 인터넷 연결이 필요합니다.

## Windows PC에서 실행

1. Python 3을 설치합니다.
2. 터미널에서 아래 명령을 실행합니다.

    python -m pip install -r pc/requirements-pygame.txt
    python pc/taehyun_rescue_pygame.py

또는 pc 폴더의 실행하기.bat를 더블 클릭합니다. 이전 Tkinter 버전은 pc/taehyun_rescue.py에 보관되어 있습니다.

온라인 API 주소는 TAEHYUN_API_URL 환경 변수로 바꿀 수 있으며 기본 주소는 https://taehyun-rescue-api.onrender.com 입니다.

## Android APK 빌드

1. GitHub 저장소의 Actions 탭을 엽니다.
2. Build Android APK 워크플로를 선택하고 Run workflow를 누릅니다.
3. 빌드가 성공하면 Artifacts에서 taehyun-rescue-apk ZIP을 내려받습니다.
4. ZIP 안의 debug APK를 Android 기기에 설치해 확인합니다.

프로젝트에는 컴파일된 APK가 포함되어 있지 않습니다. Pygame의 Android 빌드는 Python/SDL/Pygame 버전 조합에 따라 조정이 필요할 수 있으므로 빌드 완료만으로 실제 휴대폰 실행까지 보장되지는 않습니다.

## 온라인 API 서버

API 서버는 api.py입니다. Render 설정은 README_ONLINE_KO.md를 참고하세요. 비공개 환경 변수 ADMIN_USERNAME, ADMIN_PASSWORD, APP_SECRET, DATABASE_URL을 사용하며, 비밀번호나 데이터베이스 접속 주소를 GitHub 소스에 넣지 마세요.

주의: DATABASE_URL이 없으면 테스트용 임시 SQLite DB를 사용하고, 호스팅 재시작/재배포 시 데이터가 사라질 수 있습니다. 실제 계정 진행 상황을 보존하려면 영구 저장이 가능한 데이터베이스를 연결해야 합니다.
