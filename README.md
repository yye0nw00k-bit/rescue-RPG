# 태현이 구하기(?)

PC와 Android용 2D 횡스크롤 RPG 프로젝트입니다. 13개 지역을 돌파하고 마지막 보스를 물리쳐 태현이를 구출하세요.

## 플랫폼

- **Windows PC:** Python 3 + tkinter. pygame은 필요하지 않습니다.
- **Android:** Kivy 기반 프로젝트입니다. 저장소의 GitHub Actions에서 APK 빌드를 실행할 수 있습니다.
- **온라인 계정 서버:** PC 버전은 공용 API에 연결하도록 변경되었습니다. Android 버전은 현재 별도 로컬 계정 방식이므로 아직 PC 계정과 자동 연동되지 않습니다.

## PC에서 실행

1. Python 3을 설치합니다. tkinter가 포함되어 있어야 합니다.
2. `pc` 폴더에서 `실행하기.bat`을 더블 클릭하거나 실행합니다.

```bat
python taehyun_rescue.py
```

PC 버전의 온라인 로그인 주소는 `TAEHYUN_API_URL` 환경 변수로 바꿀 수 있습니다. 기본 주소는 `https://taehyun-rescue-api.onrender.com`입니다. API가 아직 배포/연결되지 않은 상태라면 로그인은 작동하지 않습니다.

## 온라인 API 서버 배포

자세한 설명은 [README_ONLINE_KO.md](README_ONLINE_KO.md)를 참고하세요.

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- 비공개 환경 변수: `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `APP_SECRET`, `DATABASE_URL`

**중요:** `DATABASE_URL`을 설정하지 않으면 API는 테스트용 임시 SQLite 데이터베이스를 사용합니다. 이 방식은 다른 기기에서 같은 계정으로 로그인하는 테스트에는 쓸 수 있지만, Render 서비스가 재배포되거나 재시작되면 데이터가 사라질 수 있습니다. 실제 사용 전에는 보존 가능한 PostgreSQL 데이터베이스를 연결하고 `/health` 응답이 `"database": "postgresql"`인지 확인하세요. 비밀번호나 데이터베이스 주소를 소스 코드에 넣지 마세요.

## Android APK 빌드

1. GitHub의 **Actions** 탭을 엽니다.
2. **Build Android APK** 워크플로를 선택합니다.
3. **Run workflow**를 눌러 빌드를 시작합니다.
4. 완료된 실행 화면의 **Artifacts**에서 `taehyun-rescue-apk`를 다운로드합니다.
5. 내려받은 ZIP 안의 APK 파일을 Android 기기에 설치해 테스트합니다.

이 저장소에는 컴파일된 APK가 포함되어 있지 않습니다. GitHub Actions가 APK를 빌드하도록 설정되어 있습니다. APK 빌드는 Android SDK/NDK와 관련 도구를 내려받고 컴파일해야 하므로 시간이 걸릴 수 있으며, 빌드 성공이 보장되는 것은 아닙니다.

## 스토리

- 13개 모험 지역과 보스
- 첫 12개 보스 이후 각기 다른 NPC가 등장해 “태현이는 여기에 없어요. 일단 이거 받으세요.”라고 말하고 보상을 줍니다.
- 최종 보스 이후 이름표가 ‘태현’인 인물이 등장해 플레이어 닉네임을 넣어 “고마워요 [닉네임], 환생할 기회를 줄게요.”라고 말합니다.
- 엔딩 후 환생으로 다시 모험할 수 있습니다.

## 계정과 저장 데이터

- PC 버전의 온라인 관리자 계정은 서버의 비공개 환경 변수에서 생성합니다. 비밀번호는 저장소에 올리지 않습니다.
- 예전 PC의 로컬 계정 데이터가 온라인 서버로 자동 이관되지는 않습니다. 새 서버에서는 계정을 새로 만들거나 별도로 이관해야 합니다.
- Android 앱은 온라인 계정 연동 작업이 별도로 필요합니다.
