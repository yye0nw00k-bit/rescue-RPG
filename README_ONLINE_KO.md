# 온라인 계정 서버 설정 안내

PC 게임은 `api.py`의 온라인 API를 사용합니다. 이 API는 회원가입/로그인, 계정 정지, 계정 목록 조회, 저장 데이터 조회·수정 기능을 제공합니다.

## Render 배포

- Repository: `https://github.com/yye0nw00k-bit/rescue-RPG`
- Branch: `main`
- Runtime: Python
- Region: Singapore
- Plan: Free
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

Render의 Environment에 다음 값을 비공개로 설정합니다.

- `ADMIN_USERNAME`: 관리자 아이디 (기본 권장값: `연욱`)
- `ADMIN_PASSWORD`: 관리자만 아는 새 비밀번호
- `APP_SECRET`: 충분히 긴 임의 문자열
- `DATABASE_URL`: 보존 가능한 PostgreSQL 데이터베이스의 connection string

`ADMIN_PASSWORD`, `APP_SECRET`, `DATABASE_URL`은 GitHub 파일에 적거나 공개 채팅에 올리지 마세요.

## 데이터 저장 관련 주의

`DATABASE_URL`이 설정되어 있으면 PostgreSQL을 사용합니다. 설정되어 있지 않으면 `/tmp`의 SQLite를 사용해 테스트 모드로 실행합니다. Render 무료 서비스의 로컬 파일은 영구 저장소가 아니므로 재시작/재배포 시 테스트 데이터가 없어질 수 있습니다. 실제로 계정을 모으기 전에 PostgreSQL을 연결하고 `/health`가 `{"ok":true,"database":"postgresql"}` 형태를 반환하는지 확인하세요.

Render 무료 Postgres는 생성 후 30일 뒤 만료될 수 있습니다. 장기간 유지할 계정 데이터를 여기에만 맡기지 마세요. 현재 Render 워크스페이스에 이미 다른 용도의 무료 데이터베이스가 있으므로, 해당 데이터베이스를 게임에 연결하기 전에는 그 앱과 데이터에 영향이 없는지 확인해야 합니다.

## PC 버전

PC 게임의 기본 API 주소는 `https://taehyun-rescue-api.onrender.com`이며, 다른 주소를 사용할 때는 `TAEHYUN_API_URL` 환경 변수를 설정합니다. 로그인 화면은 온라인 서버에 접속해야 합니다.

기존 `~/.taehyun_growing/users.json` 계정은 온라인 서버로 자동 복사되지 않습니다. 이관이 필요한 계정은 안전한 별도 절차로 처리해야 합니다.

## Android 버전

현재 `android/main.py`는 별도 로컬 계정/저장 방식을 사용합니다. PC와 Android가 같은 계정을 공유하도록 하려면 Android 코드도 이 API에 연결하는 추가 작업이 필요합니다.
