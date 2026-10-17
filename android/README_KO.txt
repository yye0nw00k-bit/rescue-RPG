태현이 구하기(?) - Pygame 공통 게임 / Android APK
=================================================

PC와 Android가 android/game_core.py의 공통 Pygame 게임 코드를 사용합니다.

포함 기능
- 13개 지역과 지역별 보스
- 보스 격파 후 다음 지역 개방 및 보상
- 최종 보스 격파 후 태현이 키우기 모드
- 밥 주기, 같이 놀기, 훈련하기, 환생
- 온라인 회원가입/로그인 및 서버 저장
- 모바일 화면 터치 버튼 / PC 키보드 조작
- 관리자 계정 관리 화면

APK 빌드
- GitHub Actions의 Build Android APK 워크플로를 실행합니다.
- 성공한 빌드의 Artifacts에서 taehyun-rescue-apk ZIP을 다운로드합니다.
- Buildozer/Pygame Android 빌드는 라이브러리 버전에 따라 추가 수정이 필요할 수 있습니다. 빌드 성공 후 실제 Android 기기에서도 확인하세요.

Windows 실행
- Python 3 설치 후: python -m pip install -r pc/requirements-pygame.txt
- 실행: python pc/taehyun_rescue_pygame.py
- 또는 pc 폴더의 실행하기.bat를 실행합니다.

온라인 계정의 관리자 비밀번호는 Render의 ADMIN_PASSWORD 환경 변수로 관리합니다. 소스 파일에 관리자 비밀번호를 기록하지 않습니다.
