천상 키우기 - Pygame 공통 게임 / Android APK
============================================

Windows PC와 Android가 android/game_core.py의 같은 Pygame 게임 코드를 사용합니다.

포함 기능
- 13개 지역과 지역별 보스
- 레벨, 경험치, 골드, 장비 강화와 물약
- 온라인 회원가입/로그인 및 서버 저장
- 모바일 터치 버튼 / PC 키보드 조작
- 관리자 계정 관리
- 최종 보스 격파 엔딩, 환생 보너스
- 애기 돌보기/밥 주기/놀기 화면은 제거됨

APK 빌드
- GitHub Actions의 Build Android APK 워크플로를 실행합니다.
- 성공한 빌드의 Artifacts에서 chunsang-raising-apk ZIP을 다운로드합니다.
- Pygame Android 빌드는 라이브러리 호환성에 따라 추가 조정이 필요할 수 있습니다. 빌드 성공 후 실제 Android 기기에서도 테스트하세요.

Windows 실행
- Python 3 설치 후: python -m pip install -r pc/requirements-pygame.txt
- 실행: python pc/chunsang_raising.py
- 또는 pc 폴더의 실행하기.bat를 실행합니다.

온라인 계정의 관리자 비밀번호는 Render의 ADMIN_PASSWORD 환경 변수로 관리합니다. 소스 파일에 비밀번호를 기록하지 않습니다.
