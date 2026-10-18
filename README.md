# 천상 키우기

Windows PC와 Android에서 같은 Pygame 게임 코드를 사용하는 2D 횡스크롤 RPG입니다. 13개 지역과 수호자 보스를 돌파하고 마지막 보스를 물리쳐 엔딩을 보세요. 최종 보스 이후에는 애기 돌보기 모드가 나오지 않으며, 엔딩 화면에서 다시 모험할 수 있습니다.

## 포함 기능

- 13개 지역, 일반 몬스터, 지역 수호자 보스
- 경험치, 레벨, 골드, 무기·방어구 강화, 물약, 동료 보너스
- 회원가입·로그인, 온라인 저장, 관리자 계정 관리
- PC 키보드와 모바일 터치 조작
- 최종 보스 격파 엔딩과 환생 보너스

## Windows PC에서 실행

1. Python 3을 설치합니다.
2. 프로젝트 폴더에서 아래 명령을 실행합니다.

    python -m pip install -r pc/requirements-pygame.txt
    python pc/chunsang_raising.py

또는 pc 폴더의 실행하기.bat을 더블 클릭합니다. 이전 Tkinter 버전은 pc/taehyun_rescue.py에 별도로 남겨 두었습니다.

## Android APK 만들기

1. GitHub 저장소의 Actions 탭을 엽니다.
2. Build Android APK 실행을 선택합니다. 코드 변경으로 자동 실행된 빌드도 사용할 수 있습니다.
3. 빌드가 성공하면 실행 결과의 Artifacts에서 chunsang-raising-apk를 다운로드합니다.
4. ZIP 압축을 풀고 APK를 Android 기기에 설치해 테스트합니다.

APK는 Android SDK/NDK와 빌드 도구로 컴파일해야 하므로, 소스 변경만으로 설치 파일이 바로 생기는 것은 아닙니다. GitHub Actions에서 APK 빌드가 성공했는지 확인해야 합니다.

## 온라인 계정 및 관리자

PC와 Android는 모두 https://taehyun-rescue-api.onrender.com 의 온라인 API를 사용합니다. 인터넷 연결이 필요합니다. 관리자 권한은 기존 API 설정을 유지하며, 비밀번호는 Render의 비공개 ADMIN_PASSWORD 환경 변수로 관리합니다. 소스 코드에 비밀번호를 쓰지 마세요.

API의 DATABASE_URL에 영구 데이터베이스가 설정되지 않았다면 계정·저장 데이터가 재배포나 재시작 이후 사라질 수 있습니다.
