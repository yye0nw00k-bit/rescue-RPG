"""태현이 구하기(?) 온라인 계정/API 서버.
Render에서는 DATABASE_URL을 설정해 PostgreSQL을 사용하세요.
DATABASE_URL이 없으면 개발 테스트용 SQLite를 사용하며, 호스팅 재배포/재시작 때 데이터가 사라질 수 있습니다.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

IS_SQLITE = not DATABASE_URL
if IS_SQLITE:
    DATABASE_URL = "sqlite:////tmp/taehyun_rescue_test.sqlite3"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

APP_SECRET = os.getenv("APP_SECRET") or secrets.token_urlsafe(48)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "연욱").strip() or "연욱"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

app = FastAPI(title="태현이 구하기 온라인 API", docs_url=None, redoc_url=None, openapi_url=None)

# Browser-based clients (web build) call this API from a separate Render static-site origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


def _run(sql: str, params: dict | None = None, *, fetchone: bool = False, fetchall: bool = False):
    with engine.begin() as conn:
        result = conn.execute(text(sql), params or {})
        if fetchone:
            row = result.mappings().first()
            return dict(row) if row else None
        if fetchall:
            return [dict(row) for row in result.mappings().all()]
        return result.rowcount


def _init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rescue_users (
                username VARCHAR(80) PRIMARY KEY,
                nickname VARCHAR(80) NOT NULL,
                password_salt VARCHAR(128) NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'player',
                banned INTEGER NOT NULL DEFAULT 0,
                created_at BIGINT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rescue_saves (
                username VARCHAR(80) PRIMARY KEY REFERENCES rescue_users(username) ON DELETE CASCADE,
                save_json TEXT NOT NULL,
                updated_at BIGINT NOT NULL
            )
        """))
    # The admin password is injected by the host's private environment, never stored in source code.
    if ADMIN_PASSWORD:
        salt = secrets.token_hex(16)
        digest = _password_digest(ADMIN_PASSWORD, salt)
        existing = _run("SELECT username FROM rescue_users WHERE username=:u", {"u": ADMIN_USERNAME}, fetchone=True)
        if existing:
            _run(
                "UPDATE rescue_users SET nickname=:n, password_salt=:s, password_hash=:h, role='admin', banned=0 WHERE username=:u",
                {"u": ADMIN_USERNAME, "n": ADMIN_USERNAME, "s": salt, "h": digest},
            )
        else:
            _run(
                "INSERT INTO rescue_users(username,nickname,password_salt,password_hash,role,banned,created_at) VALUES(:u,:n,:s,:h,'admin',0,:t)",
                {"u": ADMIN_USERNAME, "n": ADMIN_USERNAME, "s": salt, "h": digest, "t": int(time.time())},
            )


def _password_digest(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000).hex()


def _token_for(username: str) -> str:
    body = json.dumps({"sub": username, "exp": int(time.time()) + 60 * 60 * 24 * 14},
                      separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload = base64.urlsafe_b64encode(body).rstrip(b"=").decode("ascii")
    signature = hmac.new(APP_SECRET.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return payload + "." + sig


def _user_from_token(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    token = authorization[7:].strip()
    try:
        payload, provided_sig = token.split(".", 1)
        expected = base64.urlsafe_b64encode(
            hmac.new(APP_SECRET.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest()
        ).rstrip(b"=").decode("ascii")
        if not hmac.compare_digest(expected, provided_sig):
            raise ValueError("signature")
        padded = payload + "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
        if int(claims.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        row = _run("SELECT username,nickname,role,banned FROM rescue_users WHERE username=:u",
                   {"u": claims["sub"]}, fetchone=True)
        if not row:
            raise ValueError("missing user")
        if row["banned"]:
            raise HTTPException(status_code=403, detail="이 계정은 관리자에 의해 이용이 제한되었습니다.")
        return row
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="로그인 세션이 만료되었습니다. 다시 로그인해 주세요.")


def _admin_user(authorization: str | None) -> dict:
    user = _user_from_token(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 전용 기능입니다.")
    return user


def _clean_save(value: Any) -> dict:
    if not isinstance(value, dict):
        raise HTTPException(status_code=400, detail="저장 데이터 형식이 올바르지 않습니다.")
    # Game saves should be small; this also blocks accidental huge requests.
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) > 200_000:
        raise HTTPException(status_code=413, detail="저장 데이터가 너무 큽니다.")
    return value


def _save_for(username: str) -> dict:
    row = _run("SELECT save_json FROM rescue_saves WHERE username=:u", {"u": username}, fetchone=True)
    if not row:
        return {}
    try:
        value = json.loads(row["save_json"])
        return value if isinstance(value, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def _put_save(username: str, value: dict):
    payload = json.dumps(_clean_save(value), ensure_ascii=False, separators=(",", ":"))
    existing = _run("SELECT username FROM rescue_saves WHERE username=:u", {"u": username}, fetchone=True)
    if existing:
        _run("UPDATE rescue_saves SET save_json=:d, updated_at=:t WHERE username=:u",
             {"u": username, "d": payload, "t": int(time.time())})
    else:
        _run("INSERT INTO rescue_saves(username,save_json,updated_at) VALUES(:u,:d,:t)",
             {"u": username, "d": payload, "t": int(time.time())})


def _admin_profiles():
    users = _run("SELECT username,nickname,role,banned,created_at FROM rescue_users ORDER BY username", fetchall=True)
    for u in users:
        u["banned"] = bool(u["banned"])
        u["save"] = _save_for(u["username"])
    return users


@app.on_event("startup")
def startup():
    _init_db()


@app.get("/health")
def health():
    return {"ok": True, "database": "postgresql" if not IS_SQLITE else "sqlite-temporary"}


@app.post("/api/register")
async def register(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    if not 3 <= len(username) <= 18:
        raise HTTPException(status_code=400, detail="새 아이디는 3~18자로 입력해 주세요.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="비밀번호는 4자 이상이어야 합니다.")
    if any(ord(c) < 32 for c in username):
        raise HTTPException(status_code=400, detail="아이디에 사용할 수 없는 문자가 있습니다.")
    if username == ADMIN_USERNAME:
        raise HTTPException(status_code=409, detail="해당 아이디는 관리자 계정으로 예약되어 있습니다.")
    salt = secrets.token_hex(16)
    digest = _password_digest(password, salt)
    try:
        _run(
            "INSERT INTO rescue_users(username,nickname,password_salt,password_hash,role,banned,created_at) VALUES(:u,:n,:s,:h,'player',0,:t)",
            {"u": username, "n": username, "s": salt, "h": digest, "t": int(time.time())},
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    _put_save(username, {})
    return {"token": _token_for(username), "username": username, "nickname": username, "role": "player"}


@app.post("/api/login")
async def login(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    row = _run("SELECT username,nickname,password_salt,password_hash,role,banned FROM rescue_users WHERE username=:u",
               {"u": username}, fetchone=True)
    # Perform a hash even when the account doesn't exist, to make timing less informative.
    salt = row["password_salt"] if row else "fixed-timing-salt"
    digest = _password_digest(password, salt)
    if not row or not hmac.compare_digest(digest, row["password_hash"]):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    if row["banned"]:
        raise HTTPException(status_code=403, detail="이 계정은 관리자에 의해 이용이 제한되었습니다.")
    return {"token": _token_for(username), "username": username, "nickname": row["nickname"], "role": row["role"]}


@app.get("/api/save")
def get_save(authorization: str | None = Header(default=None)):
    user = _user_from_token(authorization)
    return {"save": _save_for(user["username"])}


@app.put("/api/save")
async def put_save(request: Request, authorization: str | None = Header(default=None)):
    user = _user_from_token(authorization)
    body = await request.json()
    _put_save(user["username"], body)
    return {"ok": True}


@app.get("/api/admin/users")
def admin_users(authorization: str | None = Header(default=None)):
    _admin_user(authorization)
    return {"users": _admin_profiles()}


@app.get("/api/admin/user/{username}/save")
def admin_get_save(username: str, authorization: str | None = Header(default=None)):
    _admin_user(authorization)
    exists = _run("SELECT username FROM rescue_users WHERE username=:u", {"u": username}, fetchone=True)
    if not exists:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    return {"save": _save_for(username)}


@app.put("/api/admin/user/{username}/save")
async def admin_put_save(username: str, request: Request, authorization: str | None = Header(default=None)):
    _admin_user(authorization)
    exists = _run("SELECT username FROM rescue_users WHERE username=:u", {"u": username}, fetchone=True)
    if not exists:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    body = await request.json()
    _put_save(username, body)
    return {"ok": True}


@app.post("/api/admin/user/{username}/action")
async def admin_action(username: str, request: Request, authorization: str | None = Header(default=None)):
    _admin_user(authorization)
    user = _run("SELECT username,role,banned FROM rescue_users WHERE username=:u", {"u": username}, fetchone=True)
    if not user:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    body = await request.json()
    action = str(body.get("action", ""))
    data = _save_for(username)
    if action == "toggle_ban":
        if username == ADMIN_USERNAME or user["role"] == "admin":
            raise HTTPException(status_code=400, detail="관리자 계정은 이용 제한할 수 없습니다.")
        _run("UPDATE rescue_users SET banned=:b WHERE username=:u",
             {"u": username, "b": 0 if user["banned"] else 1})
    elif action == "add_gold":
        data["gold"] = int(data.get("gold", 0)) + 1000
        _put_save(username, data)
    elif action == "add_levels":
        data["level"] = int(data.get("level", 1)) + 5
        data["attack"] = int(data.get("attack", 10)) + 15
        data["max_hp"] = int(data.get("max_hp", 100)) + 60
        data["hp"] = data["max_hp"]
        data["skill_points"] = int(data.get("skill_points", 0)) + 5
        _put_save(username, data)
    elif action == "add_items":
        data["potions"] = int(data.get("potions", 0)) + 10
        data["crystals"] = int(data.get("crystals", 0)) + 5
        _put_save(username, data)
    elif action == "reset_save":
        _put_save(username, {})
    else:
        raise HTTPException(status_code=400, detail="알 수 없는 관리자 작업입니다.")
    return {"ok": True, "users": _admin_profiles()}


@app.get("/")
def root():
    return {"name": "태현이 구하기 온라인 API", "health": "/health"}
