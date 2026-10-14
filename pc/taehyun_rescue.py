"""태현이 구하기(?) — pygame 없이 실행하는 2D 횡스크롤 RPG
실행: python taehyun_rescue.py
필요: Python 3 + tkinter (Windows Python 설치본에 대개 포함)
계정과 진행 데이터는 이 컴퓨터의 ~/.taehyun_growing 폴더에 저장됩니다.
이 파일은 독립적인 오리지널 프로토타입이며, 온라인 계정/동기화는 제공하지 않습니다.
"""
import hashlib
import json
import math
import random
import secrets
import time
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox
import os
import urllib.error
import urllib.request
from urllib.parse import quote

API_BASE = os.getenv("TAEHYUN_API_URL", "https://taehyun-rescue-api.onrender.com").rstrip("/")

APP_DIR = Path.home() / ".taehyun_growing"
APP_DIR.mkdir(exist_ok=True)
USERS_FILE = APP_DIR / "users.json"
SAVE_FILE = APP_DIR / "rescue_saves.json"
ZONE_LENGTH = 1450

# 캠페인: 각 지역의 수호 보스를 물리치면 다음 지역으로 갈 수 있습니다.
ZONES = [
    {"name":"별빛 들판", "need":1, "sky":"#91cce8", "hill":"#76b79e", "ground":"#579451", "decor":"tree", "story":"태현이를 데려간 수상한 발자국이 별빛 들판에 남아 있다.",
     "mobs":[("초록 슬라임","#75b86e",25,7,8,30),("꽃벌","#f0c45c",30,8,10,38),("도토리 도적","#a9855d",37,9,12,27)], "boss":("별빛 슬라임 대장","#4f9f8a",155,8,110,100)},
    {"name":"버섯 숲", "need":3, "sky":"#9fcdb5", "hill":"#679a70", "ground":"#50804d", "decor":"mushroom", "story":"버섯 병사들이 숲속 길을 막고 있다.",
     "mobs":[("주황 버섯","#d98a5c",48,10,12,28),("버섯 병사","#c96561",60,12,15,25),("덩굴 벌레","#7ea85d",54,11,14,34)], "boss":("버섯 대장","#bd655d",260,11,135,170)},
    {"name":"바람 절벽", "need":5, "sky":"#b4dbe7", "hill":"#77a7b7", "ground":"#6b936b", "decor":"cliff", "story":"강한 바람을 뚫고 절벽 정상에 올라야 한다.",
     "mobs":[("바람 까마귀","#596b7a",65,12,16,46),("절벽 도마뱀","#77a56e",73,13,18,32),("바람 정령","#b9e7ed",82,14,20,40)], "boss":("회오리 수호자","#72b8c9",370,14,165,240)},
    {"name":"유령 폐광", "need":7, "sky":"#8899b5", "hill":"#66748e", "ground":"#625d69", "decor":"mine", "story":"폐광 깊은 곳에서 태현이의 흔적이 적힌 쪽지를 찾았다.",
     "mobs":[("광산 박쥐","#847eb4",82,14,20,43),("작은 유령","#b6d2d8",95,15,22,31),("철광 골렘","#7f8798",112,17,25,22)], "boss":("폐광의 망령","#9384c4",500,17,210,320)},
    {"name":"고대 유적", "need":9, "sky":"#c4b99a", "hill":"#8c9475", "ground":"#87704e", "decor":"ruin", "story":"오래된 유적의 석판에는 열세 개의 관문이 그려져 있다.",
     "mobs":[("유적 수호병","#b5a17b",116,17,26,27),("모래 벌레","#b9a46f",125,18,29,35),("고대 석상","#777c72",140,19,31,22)], "boss":("봉인된 석상왕","#a49c83",670,20,270,410)},
    {"name":"불타는 협곡", "need":12, "sky":"#dbac8a", "hill":"#a36c5f", "ground":"#735047", "decor":"lava", "story":"불길을 건너면 바닷길로 이어지는 오래된 다리가 있다.",
     "mobs":[("화염 도마뱀","#e77b47",142,20,31,36),("바위 투사","#9c7968",159,22,34,26),("불꽃 정령","#f2a04d",151,21,32,41)], "boss":("화염 골렘","#d75b44",850,24,340,500)},
    {"name":"물결 해안", "need":15, "sky":"#8bcbd7", "hill":"#5caa9e", "ground":"#408b78", "decor":"beach", "story":"파도 소리 너머에서 누군가 도움을 요청하는 소리가 들린다.",
     "mobs":[("조개 전사","#d6b6a0",170,23,36,25),("파도 게","#d66f68",186,24,39,30),("바다 정령","#77c7d5",198,25,42,38)], "boss":("폭풍 해신","#4b9eae",1060,27,410,600)},
    {"name":"얼음 성채", "need":18, "sky":"#9bbfdf", "hill":"#7595b8", "ground":"#91b6cc", "decor":"ice", "story":"얼어붙은 성채의 수호자를 넘어야 구름 위로 갈 수 있다.",
     "mobs":[("눈보라 늑대","#9cb8d7",210,26,43,42),("얼음 정령","#69c8d9",225,27,45,35),("서리 골렘","#869dc5",242,29,48,25)], "boss":("빙결 기사","#79a8d8",1300,30,500,720)},
    {"name":"구름 신전", "need":21, "sky":"#c7dcf0", "hill":"#8eacd3", "ground":"#b6c8d9", "decor":"cloud", "story":"구름 신전의 문지기가 마왕의 부하가 지나간 방향을 알려준다.",
     "mobs":[("구름 까마귀","#7f8ab6",250,29,51,43),("번개 수도사","#b6c5e2",272,30,54,28),("천둥 정령","#79b6d9",290,32,57,36)], "boss":("천공의 문지기","#6b83bf",1600,33,580,850)},
    {"name":"저주받은 늪", "need":24, "sky":"#9aaa91", "hill":"#647d66", "ground":"#596a4e", "decor":"swamp", "story":"늪지의 독안개 속에서 감옥으로 통하는 표식을 발견했다.",
     "mobs":[("늪 독개구리","#9ab65d",295,32,60,30),("독안개 유령","#90a38d",315,34,63,35),("가시 덩굴괴물","#657b55",342,35,66,24)], "boss":("늪의 저주술사","#738d64",1950,36,700,1000)},
    {"name":"수정 동굴", "need":27, "sky":"#a2b4d8", "hill":"#6e7fb5", "ground":"#526489", "decor":"crystal", "story":"빛나는 수정 속에 마지막 성의 위치가 비친다.",
     "mobs":[("수정 박쥐","#a7b7ed",350,36,68,44),("보랏빛 골렘","#8475b3",375,38,72,24),("결정 정령","#8bd5dd",398,39,76,35)], "boss":("수정 심장","#847ee2",2300,40,850,1200)},
    {"name":"그림자 성", "need":30, "sky":"#626e8a", "hill":"#42455f", "ground":"#393d50", "decor":"castle", "story":"성 안쪽에서 태현이를 가둔 마왕이 마지막 문을 지키고 있다는 사실을 알았다.",
     "mobs":[("그림자 망령","#7861a0",410,40,78,39),("검은 기사","#52566a",445,42,83,28),("저주받은 까마귀","#4a4764",390,39,75,46)], "boss":("그림자 왕","#625183",2800,43,1050,1450)},
    {"name":"어둠의 감옥", "need":34, "sky":"#383b50", "hill":"#292b3d", "ground":"#292632", "decor":"dungeon", "story":"마지막 문 뒤에 태현이가 갇혀 있다. 감금의 마왕을 쓰러뜨리자!",
     "mobs":[("감옥 경비병","#78616c",475,43,88,30),("어둠의 불꽃","#a05d78",450,42,85,45),("저주 골렘","#55516b",515,45,95,24)], "boss":("감금의 마왕","#bd4764",3600,47,1500,2200)},
]
POST_BOSS_NPCS = [
    "길 잃은 모험가", "숲의 정찰병", "절벽 안내인", "폐광 광부", "유적 연구원", "협곡 상인",
    "해안 탐험가", "얼음 사제", "구름 신전의 수련생", "늪지 약초꾼", "수정 동굴의 연구원", "성에서 탈출한 기사",
]

WORLD_WIDTH = ZONE_LENGTH * len(ZONES)


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return default


def write_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def api_request(path, method="GET", payload=None, token=None, timeout=25):
    """공용 계정 서버 요청. API 주소는 TAEHYUN_API_URL 환경 변수로 바꿀 수 있습니다."""
    url = API_BASE + path
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
            detail = body.get("detail", "서버에서 요청을 거부했습니다.")
        except Exception:
            detail = "서버에서 요청을 거부했습니다."
        raise RuntimeError(str(detail)) from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("온라인 서버에 연결할 수 없습니다. 서버가 깨어날 때까지 잠시 후 다시 시도해 주세요.") from exc


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 180_000).hex()
    return salt, digest


def default_save():
    return {
        "player_x": 160.0, "level": 1, "exp": 0, "gold": 0,
        "attack": 10, "max_hp": 100, "hp": 100, "kills": 0,
        "weapon_level": 0, "armor_level": 0, "potions": 3, "crystals": 0,
        "boss_kills": 0, "cleared_zones": [False] * len(ZONES),
        "checkpoint_zone": 0, "skill_points": 0,
        "skill_levels": {"power": 0, "vitality": 0},
        "claimed_quests": [], "achievements": [], "pets": [],
        "daily_claim": "", "game_clear": False, "rebirth_count": 0, "current_dialogue": None,
        "taehyun_hunger": 25.0, "taehyun_happiness": 70.0,
        "taehyun_level": 1, "taehyun_exp": 0, "taehyun_feed_count": 0, "taehyun_play_count": 0,
    }


class TaehyunRescue:
    def __init__(self, root):
        self.root = root
        root.title("태현이 구하기(?)")
        root.geometry("1180x760")
        root.minsize(800, 600)
        root.configure(bg="#151b29")
        self.users = read_json(USERS_FILE, {})
        self.saves = read_json(SAVE_FILE, {})
        self.seed_admin_account()
        self.current_user = None
        self.api_token = None
        self.admin_saves = {}
        self.nickname, self.role, self.mode = "", "player", "login"
        self.frame = self.canvas = None
        self.tick_session = 0
        self.keys = set()
        self.monsters = []
        self.particles = []
        self.active_panel = None
        self.auto_attack = False
        self.player_x, self.jump_height, self.jump_v = 160.0, 0.0, 0.0
        self.on_ground, self.facing = True, 1
        self.level, self.exp, self.gold, self.attack = 1, 0, 0, 10
        self.max_hp, self.hp, self.kills = 100, 100, 0
        self.weapon_level = self.armor_level = self.potions = self.crystals = self.boss_kills = 0
        self.cleared_zones = [False] * len(ZONES)
        self.checkpoint_zone = 0
        self.skill_points = 0
        self.skill_levels = {"power": 0, "vitality": 0}
        self.claimed_quests, self.achievements, self.pets = [], [], []
        self.game_clear = False
        self.rebirth_count = 0
        self.current_dialogue = None
        self.taehyun_hunger, self.taehyun_happiness = 25.0, 70.0
        self.taehyun_level, self.taehyun_exp = 1, 0
        self.taehyun_feed_count = self.taehyun_play_count = 0
        self._save_upload_lock = threading.Lock()
        self.last_tick = time.perf_counter()
        self.last_save = time.time()
        self.last_attack = 0.0
        self.last_hit = 0.0
        self.monster_timer = 0.0
        self.skill_cooldowns = {1: 0.0, 2: 0.0, 3: 0.0}
        self.message, self.message_until = "", 0
        self.admin_targets, self.admin_target_index = [], 0
        self.show_auth()
        root.protocol("WM_DELETE_WINDOW", self.close)

    # -------------------------- 계정과 저장 --------------------------
    def seed_admin_account(self):
        # 온라인 관리자 계정은 api.py의 비공개 Render 환경 변수로만 생성합니다.
        # 이 PC에 하드코딩된 관리자 비밀번호를 다시 만들지 않습니다.
        self.users = read_json(USERS_FILE, {})

    def set_message(self, text, seconds=3):
        self.message, self.message_until = str(text), time.time() + seconds

    def show_auth(self):
        if self.frame:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg="#151b29")
        self.frame.pack(fill="both", expand=True)
        card = tk.Frame(self.frame, bg="#202a3c", padx=34, pady=25,
                        highlightbackground="#4e6687", highlightthickness=1)
        card.place(relx=.5, rely=.48, anchor="center", width=500, height=535)
        tk.Label(card, text="태현이 구하기(?)", bg="#202a3c", fg="#ffdf91",
                 font=("Malgun Gothic", 25, "bold")).pack(pady=(7, 2))
        tk.Label(card, text="한 지역씩 돌파하고, 마지막 마왕에게서 태현이를 구하자!",
                 bg="#202a3c", fg="#b0bfd4", font=("Malgun Gothic", 10), wraplength=400).pack(pady=(0, 17))
        row = tk.Frame(card, bg="#202a3c")
        row.pack(fill="x", pady=(0, 12))
        self.login_mode_btn = tk.Button(row, text="로그인", command=lambda: self.set_mode("login"),
            bg="#34547a", fg="white", relief="flat", font=("Malgun Gothic", 10), pady=7)
        self.login_mode_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.signup_mode_btn = tk.Button(row, text="회원가입", command=lambda: self.set_mode("signup"),
            bg="#2b374a", fg="white", relief="flat", font=("Malgun Gothic", 10), pady=7)
        self.signup_mode_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        tk.Label(card, text="아이디", bg="#202a3c", fg="#dce5f1", anchor="w").pack(fill="x", pady=(7, 5))
        self.username_entry = tk.Entry(card, font=("Malgun Gothic", 12), relief="flat", bg="#111723",
                                       fg="white", insertbackground="white")
        self.username_entry.pack(fill="x", ipady=8)
        tk.Label(card, text="비밀번호", bg="#202a3c", fg="#dce5f1", anchor="w").pack(fill="x", pady=(12, 5))
        self.password_entry = tk.Entry(card, show="●", font=("Malgun Gothic", 12), relief="flat",
                                       bg="#111723", fg="white", insertbackground="white")
        self.password_entry.pack(fill="x", ipady=8)
        self.submit_btn = tk.Button(card, text="로그인하고 시작", command=self.submit_auth, bg="#ba934a",
            fg="#171b25", activebackground="#d1ad65", relief="flat",
            font=("Malgun Gothic", 11, "bold"), pady=10)
        self.submit_btn.pack(fill="x", pady=(19, 10))
        self.auth_message = tk.Label(card, text="계정과 게임 데이터는 온라인 서버에 저장됩니다.", bg="#202a3c",
            fg="#a8b5c8", wraplength=400, font=("Malgun Gothic", 9))
        self.auth_message.pack(pady=(0, 3))
        tk.Label(card, text="온라인 계정 · 기기 간 진행 상황 동기화", bg="#202a3c", fg="#d6bd85",
                 font=("Malgun Gothic", 9)).pack(pady=(10, 0))
        tk.Label(card, text="처음 접속할 때 서버 연결에 시간이 걸릴 수 있습니다.", bg="#202a3c", fg="#8292aa",
                 font=("Malgun Gothic", 9)).pack(pady=(5, 0))
        self.username_entry.bind("<Return>", lambda _e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda _e: self.submit_auth())
        self.username_entry.focus_set()
        self.set_mode(self.mode)

    def set_mode(self, mode):
        self.mode = mode
        self.login_mode_btn.configure(bg="#34547a" if mode == "login" else "#2b374a")
        self.signup_mode_btn.configure(bg="#34547a" if mode == "signup" else "#2b374a")
        self.submit_btn.configure(text="로그인하고 시작" if mode == "login" else "계정 만들기")
        self.auth_message.configure(text="아이디와 비밀번호를 입력해 주세요.", fg="#a8b5c8")

    def auth_error(self, text):
        self.auth_message.configure(text=text, fg="#ffaaa0")

    def submit_auth(self):
        name, password = self.username_entry.get().strip(), self.password_entry.get()
        if not name or not password:
            return self.auth_error("아이디와 비밀번호를 입력해 주세요.")
        endpoint = "/api/register" if self.mode == "signup" else "/api/login"
        self.submit_btn.configure(state="disabled")
        try:
            result = api_request(endpoint, method="POST", payload={"username": name, "password": password})
        except RuntimeError as exc:
            self.submit_btn.configure(state="normal")
            return self.auth_error(str(exc))
        finally:
            try:
                self.submit_btn.configure(state="normal")
            except tk.TclError:
                pass
        self.api_token = result.get("token")
        self.current_user = result.get("username", name)
        self.nickname = result.get("nickname", self.current_user)
        self.role = result.get("role", "player")
        self.load_game(self.current_user)
        self.show_game()
        if self.game_clear:
            self.set_message("태현이 구출 완료! 다시 모험하거나 기록을 확인하세요.", 5)
        elif self.message == "":
            self.set_message("온라인 계정으로 모험을 시작합니다!")

    def load_game(self, name):
        self.saves = read_json(SAVE_FILE, {})
        data = default_save()
        saved = self.saves.get(name, {})
        if self.api_token:
            try:
                saved = api_request("/api/save", token=self.api_token).get("save", {})
                if not isinstance(saved, dict):
                    saved = {}
                self.saves[name] = saved
                write_json(SAVE_FILE, self.saves)
            except RuntimeError as exc:
                self.set_message("서버 저장 데이터를 읽지 못했습니다: " + str(exc), 6)
        if isinstance(saved, dict):
            data.update(saved)
        # 기존 7지역 버전의 저장 파일은 13지역 캠페인과 구조가 다르므로 새 모험 진행만 초기화합니다.
        old_clear_flags = saved.get("cleared_zones", []) if isinstance(saved, dict) else []
        if old_clear_flags and len(old_clear_flags) != len(ZONES):
            data["cleared_zones"] = [False] * len(ZONES)
            data["game_clear"] = False
            data["player_x"] = 160.0
            data["checkpoint_zone"] = 0
            data["boss_kills"] = 0
            data["current_dialogue"] = None
        self.level = max(1, int(data.get("level", 1)))
        self.exp = max(0, int(data.get("exp", 0)))
        self.gold = max(0, int(data.get("gold", 0)))
        self.attack = max(1, int(data.get("attack", 10)))
        self.max_hp = max(1, int(data.get("max_hp", 100)))
        self.hp = max(1, min(self.max_hp, int(data.get("hp", self.max_hp))))
        self.kills = max(0, int(data.get("kills", 0)))
        self.weapon_level = max(0, int(data.get("weapon_level", 0)))
        self.armor_level = max(0, int(data.get("armor_level", 0)))
        self.potions = max(0, int(data.get("potions", 3)))
        self.crystals = max(0, int(data.get("crystals", 0)))
        self.boss_kills = max(0, int(data.get("boss_kills", 0)))
        clears = list(data.get("cleared_zones", []))
        self.cleared_zones = (clears + [False] * len(ZONES))[:len(ZONES)]
        self.checkpoint_zone = max(0, min(len(ZONES)-1, int(data.get("checkpoint_zone", 0))))
        self.skill_points = max(0, int(data.get("skill_points", 0)))
        self.skill_levels = {"power": 0, "vitality": 0}
        self.skill_levels.update(data.get("skill_levels", {}))
        self.claimed_quests = list(data.get("claimed_quests", []))
        self.achievements = list(data.get("achievements", []))
        self.pets = list(data.get("pets", []))
        self.game_clear = bool(data.get("game_clear", False))
        self.taehyun_hunger = max(0.0, min(100.0, float(data.get("taehyun_hunger", 25))))
        self.taehyun_happiness = max(0.0, min(100.0, float(data.get("taehyun_happiness", 70))))
        self.taehyun_level = max(1, int(data.get("taehyun_level", 1)))
        self.taehyun_exp = max(0, int(data.get("taehyun_exp", 0)))
        self.taehyun_feed_count = max(0, int(data.get("taehyun_feed_count", 0)))
        self.taehyun_play_count = max(0, int(data.get("taehyun_play_count", 0)))
        self.rebirth_count = max(0, int(data.get("rebirth_count", 0)))
        self.current_dialogue = data.get("current_dialogue")
        self.player_x = float(data.get("player_x", 160))
        self.player_x = max(40, min(WORLD_WIDTH-40, self.player_x))
        self.jump_height = self.jump_v = 0.0
        self.on_ground, self.facing = True, 1
        self.monsters, self.particles = [], []
        self.monster_timer = 0.0
        self.auto_attack = False
        self.active_panel = "raising" if self.game_clear else ("dialogue" if self.current_dialogue else None)
        self.skill_cooldowns = {1: 0.0, 2: 0.0, 3: 0.0}
        self.last_attack = self.last_hit = 0.0
        self._daily_claim = str(data.get("daily_claim", ""))
        today = date.today().isoformat()
        if self._daily_claim != today:
            self.gold += 100 + self.level * 10
            self.potions += 2
            self._daily_claim = today
            self.set_message("접속 보상! 골드와 회복 물약을 받았습니다.", 4)
        zone = self.zone_index_for(self.player_x)
        if zone > 0 and not self.cleared_zones[zone-1]:
            self.player_x = 160.0
        self.last_tick = time.perf_counter()

    def save_payload(self):
        return {
            "player_x": self.player_x, "level": self.level, "exp": self.exp, "gold": self.gold,
            "attack": self.attack, "max_hp": self.max_hp, "hp": self.hp, "kills": self.kills,
            "weapon_level": self.weapon_level, "armor_level": self.armor_level,
            "potions": self.potions, "crystals": self.crystals, "boss_kills": self.boss_kills,
            "cleared_zones": self.cleared_zones, "checkpoint_zone": self.checkpoint_zone,
            "skill_points": self.skill_points, "skill_levels": self.skill_levels,
            "claimed_quests": self.claimed_quests, "achievements": self.achievements,
            "pets": self.pets, "daily_claim": self._daily_claim, "game_clear": self.game_clear,
            "rebirth_count": self.rebirth_count, "current_dialogue": self.current_dialogue,
            "taehyun_hunger": self.taehyun_hunger, "taehyun_happiness": self.taehyun_happiness,
            "taehyun_level": self.taehyun_level, "taehyun_exp": self.taehyun_exp,
            "taehyun_feed_count": self.taehyun_feed_count, "taehyun_play_count": self.taehyun_play_count,
        }

    def save_game(self, exiting=False):
        if not self.current_user:
            return
        self.saves = read_json(SAVE_FILE, {})
        payload = self.save_payload()
        self.saves[self.current_user] = payload
        write_json(SAVE_FILE, self.saves)  # 서버 장애 시를 위한 이 PC의 임시 백업
        if self.api_token:
            snapshot = json.loads(json.dumps(payload, ensure_ascii=False))
            threading.Thread(target=self._upload_save_background,
                             args=(self.api_token, snapshot), daemon=True).start()
        self.last_save = time.time()

    def _upload_save_background(self, token, payload):
        if not self._save_upload_lock.acquire(blocking=False):
            return
        try:
            api_request("/api/save", method="PUT", payload=payload, token=token, timeout=4)
        except RuntimeError:
            pass
        finally:
            self._save_upload_lock.release()

    def logout(self):
        self.tick_session += 1
        self.save_game(exiting=True)
        self.current_user = None
        self.api_token = None
        self.keys.clear()
        self.root.unbind_all("<KeyPress>")
        self.root.unbind_all("<KeyRelease>")
        self.show_auth()

    def close(self):
        self.tick_session += 1
        self.save_game(exiting=True)
        self.root.destroy()

    # -------------------------- 진행과 성장 --------------------------
    @property
    def current_zone_index(self):
        return self.zone_index_for(self.player_x)

    @property
    def current_zone(self):
        return ZONES[self.current_zone_index]

    @property
    def total_attack(self):
        return self.attack + self.weapon_level * 5 + len(self.pets) * 2 + self.skill_levels.get("power", 0) * 3

    @property
    def total_defense(self):
        return self.armor_level * 2 + len(self.pets)

    def zone_index_for(self, x):
        return max(0, min(len(ZONES)-1, int(max(0, x) // ZONE_LENGTH)))

    def zone_available(self, idx):
        if idx < 0 or idx >= len(ZONES) or self.level < ZONES[idx]["need"]:
            return False
        return all(self.cleared_zones[j] for j in range(idx))

    def cleared_count(self):
        return sum(1 for v in self.cleared_zones if v)

    def gain_exp(self, amount):
        self.exp += int(amount)
        levels_gained = 0
        while self.exp >= self.level * 30:
            self.exp -= self.level * 30
            self.level += 1
            self.attack += 3
            self.max_hp += 12
            self.hp = self.max_hp
            self.skill_points += 1
            levels_gained += 1
        if levels_gained:
            self.set_message(f"레벨 업! Lv.{self.level} · 스킬 포인트 +{levels_gained}")
        self.check_achievements()

    def spawn_monster(self, sw):
        zi = self.current_zone_index
        zone = ZONES[zi]
        if any(m.get("zone_boss") for m in self.monsters):
            return
        if len(self.monsters) >= 6:
            return
        left, right = zi * ZONE_LENGTH + 120, (zi+1) * ZONE_LENGTH - 500
        if right <= left:
            return
        if self.player_x < (left + right) / 2:
            x = min(right, self.player_x + sw * .58 + random.randint(30, 160))
        else:
            x = max(left, self.player_x - sw * .58 - random.randint(30, 160))
        x = max(left, min(right, x))
        name, color, base_hp, damage, reward, speed = random.choice(zone["mobs"])
        hp = base_hp + max(0, self.level-zone["need"]) * 3
        self.monsters.append({"x": x, "name": name, "color": color, "hp": hp, "max_hp": hp,
            "speed": speed + min(12, self.level) * .35, "damage": max(2, damage + self.level//5),
            "exp": reward + self.level*2, "gold": reward + self.level*2,
            "flash": 0.0, "boss": False, "zone_boss": False, "attack_cd": random.uniform(.2, .8)})

    def spawn_zone_boss(self, idx):
        if self.cleared_zones[idx] or any(m.get("zone_boss") for m in self.monsters):
            return
        zone = ZONES[idx]
        name, color, hp, damage, exp_reward, gold_reward = zone["boss"]
        x = (idx+1) * ZONE_LENGTH - 245
        # 후반부일수록 체력이 크게 오르되 장비 성장과 자동 공격으로 공략할 수 있도록 조정
        self.monsters.clear()
        self.monsters.append({"x": x, "name": name, "color": color, "hp": hp, "max_hp": hp,
            "speed": 22 + idx*2, "damage": damage, "exp": exp_reward, "gold": gold_reward,
            "flash": 0.0, "boss": True, "zone_boss": True, "zone_index": idx,
            "attack_cd": .6, "phase": 0.0})
        self.monster_timer = 0.0
        self.set_message(f"지역 수호자 등장: {name}! 자동 공격(F)과 물약(H)을 활용하세요.", 4)

    def attack_nearby(self, multiplier=1.0, all_nearby=False, skill_name=None):
        now = time.perf_counter()
        if now - self.last_attack < .36:
            return
        self.last_attack = now
        max_range = 220 if any(abs(m["x"]-self.player_x) < 250 and m.get("boss") for m in self.monsters) else 150
        nearby = [m for m in self.monsters if abs(m["x"]-self.player_x) <= (220 if m.get("boss") else max_range)]
        if not nearby:
            if skill_name:
                self.set_message("공격 범위 안에 적이 없습니다.", 1.2)
            return
        targets = nearby if all_nearby else [min(nearby, key=lambda m: abs(m["x"]-self.player_x))]
        for target in list(targets):
            damage = max(1, int((self.total_attack + random.randint(0, max(1, self.level//3))) * multiplier))
            target["hp"] -= damage
            target["flash"] = .18
            self.particles.append({"x": target["x"], "life": .55, "text": f"-{damage}", "rise": 0})
            if target["hp"] <= 0 and target in self.monsters:
                self.defeat_monster(target)
        if skill_name:
            self.set_message(f"{skill_name}!", 1.1)

    def defeat_monster(self, monster):
        if monster not in self.monsters:
            return
        self.monsters.remove(monster)
        self.gold += int(monster["gold"])
        self.kills += 1
        if monster.get("zone_boss"):
            idx = int(monster.get("zone_index", self.current_zone_index))
            self.boss_kills += 1
            self.cleared_zones[idx] = True
            self.checkpoint_zone = min(len(ZONES)-1, idx+1)
            self.potions += 2
            self.crystals += random.randint(2, 4) + idx
            self.gain_exp(monster["exp"])
            self.set_message(f"{monster['name']} 격파! {ZONES[idx]['name']} 클리어! 다음 길이 열렸습니다.", 5)
            if self.boss_kills == 1 and "꼬마 슬라임" not in self.pets:
                self.pets.append("꼬마 슬라임")
                self.set_message("첫 보스 보상: 동료 '꼬마 슬라임' 합류! 공격력과 방어력이 상승합니다.", 5)
            elif self.boss_kills == 3 and "불꽃 여우" not in self.pets:
                self.pets.append("불꽃 여우")
                self.set_message("세 번째 보스 보상: 동료 '불꽃 여우' 합류!", 5)
            elif self.boss_kills == 5 and "얼음 정령 친구" not in self.pets:
                self.pets.append("얼음 정령 친구")
                self.set_message("다섯 번째 보스 보상: 동료 '얼음 정령 친구' 합류!", 5)
            self.hp = self.max_hp
            if idx < len(ZONES)-1:
                self.player_x = (idx+1)*ZONE_LENGTH - 95
                npc_name = POST_BOSS_NPCS[idx]
                # 지역 보스마다 다른 인물이 등장하지만 태현이는 아직 발견되지 않습니다.
                bonus_gold = 100 + idx * 75
                self.gold += bonus_gold
                self.potions += 1
                self.crystals += 1
                self.current_dialogue = {
                    "kind": "npc", "name": npc_name,
                    "line": "태현이는 여기에 없어요. 일단 이거 받으세요.",
                    "reward": f"보상: 골드 {bonus_gold} · 회복 물약 1개 · 강화 수정 1개",
                    "zone": idx + 1,
                }
                self.active_panel = "dialogue"
                self.set_message(f"{npc_name}이(가) 나타났습니다.", 3)
            else:
                self.game_clear = True
                self.hp = self.max_hp
                self.player_x = WORLD_WIDTH - 300
                self.current_dialogue = {
                    "kind": "final", "name": "태현",
                    "line": f"고마워요 {self.nickname}, 환생할 기회를 줄게요.",
                    "reward": "태현이를 구출했습니다! 원한다면 환생하여 더 강해질 수 있습니다.",
                    "zone": len(ZONES),
                }
                self.active_panel = "raising"
                self.root.title("태현이 키우기")
                self.save_game()
                self.set_message("태현이 구출 완료! 이제 태현이 키우기가 시작됩니다.", 8)
            self.check_achievements()
        else:
            if random.random() < .16:
                self.potions += 1
                self.set_message("몬스터가 회복 물약을 떨어뜨렸습니다!", 1.4)
            if random.random() < .15:
                self.crystals += 1
                self.set_message("강화 수정을 획득했습니다!", 1.4)
            self.gain_exp(monster["exp"])
            if self.kills % 10 == 0:
                self.gold += 35
                self.gain_exp(15)
                self.set_message("몬스터 10마리 처치 보너스! 골드와 경험치를 받았습니다.", 2.5)
        self.check_achievements()

    def use_skill(self, skill):
        now = time.perf_counter()
        if self.active_panel:
            return
        if skill == 1:
            if now < self.skill_cooldowns[1]:
                return self.set_message("번개 베기가 아직 재사용 대기 중입니다.", 1.3)
            if not any(abs(m["x"]-self.player_x) < 230 for m in self.monsters):
                return self.set_message("번개 베기 범위 안에 적이 없습니다.", 1.3)
            self.skill_cooldowns[1] = now + 3.5
            self.attack_nearby(2.2, skill_name="번개 베기")
        elif skill == 2:
            if self.level < 3:
                return self.set_message("회복 기운은 레벨 3부터 사용할 수 있습니다.")
            if now < self.skill_cooldowns[2]:
                return self.set_message("회복 기운이 아직 재사용 대기 중입니다.", 1.3)
            if self.hp >= self.max_hp:
                return self.set_message("체력이 이미 가득 찼습니다.", 1.3)
            self.skill_cooldowns[2] = now + 10
            healed = min(int(self.max_hp*.35)+10, self.max_hp-self.hp)
            self.hp += healed
            self.set_message(f"회복 기운! HP +{healed}")
        elif skill == 3:
            if self.level < 7:
                return self.set_message("폭풍 일격은 레벨 7부터 사용할 수 있습니다.")
            if now < self.skill_cooldowns[3]:
                return self.set_message("폭풍 일격이 아직 재사용 대기 중입니다.", 1.3)
            if not any(abs(m["x"]-self.player_x) < 260 for m in self.monsters):
                return self.set_message("폭풍 일격 범위 안에 적이 없습니다.", 1.3)
            self.skill_cooldowns[3] = now + 8
            self.attack_nearby(1.25, all_nearby=True, skill_name="폭풍 일격")

    def upgrade_attack(self):
        cost = self.level * 30
        if self.gold < cost:
            return self.set_message("골드가 부족합니다.")
        self.gold -= cost
        self.attack += 5
        self.set_message("기본 공격력이 5 올랐습니다!")

    def upgrade_hp(self):
        cost = self.level * 25
        if self.gold < cost:
            return self.set_message("골드가 부족합니다.")
        self.gold -= cost
        self.max_hp += 25
        self.hp = self.max_hp
        self.set_message("최대 HP가 25 올랐습니다!")

    def upgrade_weapon(self):
        cost = 80 + self.weapon_level * 95
        if self.gold < cost:
            return self.set_message("골드가 부족합니다.")
        self.gold -= cost
        if self.crystals > 0:
            self.crystals -= 1
            self.weapon_level += 2
            self.set_message(f"수정 강화 성공! 무기 +{self.weapon_level}")
        else:
            self.weapon_level += 1
            self.set_message(f"무기 강화 성공! 무기 +{self.weapon_level}")

    def upgrade_armor(self):
        cost = 70 + self.armor_level * 85
        if self.gold < cost:
            return self.set_message("골드가 부족합니다.")
        self.gold -= cost
        if self.crystals > 0:
            self.crystals -= 1
            self.armor_level += 2
            self.set_message(f"수정 강화 성공! 방어구 +{self.armor_level}")
        else:
            self.armor_level += 1
            self.set_message(f"방어구 강화 성공! 방어구 +{self.armor_level}")

    def buy_item(self, item):
        costs = {"potion": 25, "crystal": 115, "scroll": 175}
        cost = costs[item]
        if self.gold < cost:
            return self.set_message("골드가 부족합니다.")
        self.gold -= cost
        if item == "potion":
            self.potions += 1
            self.set_message("회복 물약 1개를 구매했습니다.")
        elif item == "crystal":
            self.crystals += 1
            self.set_message("강화 수정 1개를 구매했습니다.")
        else:
            self.attack += 10
            self.set_message("공격 주문서 사용! 공격력 +10")

    def use_potion(self):
        if self.potions <= 0:
            return self.set_message("물약이 없습니다. 상점(K)에서 구매하세요.")
        if self.hp >= self.max_hp:
            return self.set_message("체력이 이미 가득 찼습니다.")
        self.potions -= 1
        healed = min(60 + self.level*2, self.max_hp-self.hp)
        self.hp += healed
        self.set_message(f"회복 물약 사용! HP +{healed}")

    def buy_passive(self, stat):
        if self.skill_points <= 0:
            return self.set_message("스킬 포인트가 부족합니다. 레벨업으로 얻을 수 있어요.")
        self.skill_points -= 1
        if stat == "power":
            self.skill_levels["power"] += 1
            self.set_message("검술 훈련! 공격력이 영구적으로 3 상승합니다.")
        else:
            self.skill_levels["vitality"] += 1
            self.max_hp += 30
            self.hp = min(self.max_hp, self.hp+30)
            self.set_message("튼튼한 체력! 최대 HP가 30 상승합니다.")

    # -------------------------- 임무 / 업적 --------------------------
    def quest_data(self):
        return [
            {"id":"kills10", "name":"첫 사냥", "desc":"몬스터 10마리 처치", "progress":min(10,self.kills), "goal":10, "gold":150, "exp":35},
            {"id":"kills50", "name":"숙련 사냥꾼", "desc":"몬스터 50마리 처치", "progress":min(50,self.kills), "goal":50, "gold":500, "exp":100},
            {"id":"level5", "name":"성장하는 모험가", "desc":"레벨 5 달성", "progress":min(5,self.level), "goal":5, "gold":250, "exp":55},
            {"id":"level15", "name":"강해진 구조대원", "desc":"레벨 15 달성", "progress":min(15,self.level), "goal":15, "gold":600, "exp":150},
            {"id":"stage1", "name":"첫 번째 문", "desc":"지역 보스 1명 처치", "progress":min(1,self.boss_kills), "goal":1, "gold":200, "exp":60},
            {"id":"stage3", "name":"깊은 모험", "desc":"지역 3개 클리어", "progress":min(3,self.cleared_count()), "goal":3, "gold":550, "exp":125},
            {"id":"crystals", "name":"강화 재료 수집", "desc":"강화 수정 5개 보유", "progress":min(5,self.crystals), "goal":5, "gold":180, "exp":45},
            {"id":"rescue", "name":"태현이 구출 작전", "desc":"최종 보스 처치 및 구출", "progress":1 if self.game_clear else 0, "goal":1, "gold":2000, "exp":500},
        ]

    def claim_quest(self, qid):
        quest = next((q for q in self.quest_data() if q["id"] == qid), None)
        if not quest or qid in self.claimed_quests:
            return
        if quest["progress"] < quest["goal"]:
            return self.set_message("아직 임무 목표를 달성하지 못했습니다.")
        self.claimed_quests.append(qid)
        self.gold += quest["gold"]
        self.gain_exp(quest["exp"])
        self.set_message(f"임무 보상! {quest['gold']} 골드와 EXP {quest['exp']} 획득")

    def achievement_data(self):
        return [
            ("first_kill", "첫 승리", "몬스터를 처음 처치", self.kills >= 1, 50),
            ("slayer25", "사냥꾼", "몬스터 25마리 처치", self.kills >= 25, 180),
            ("boss1", "수호자 돌파", "지역 보스 첫 처치", self.boss_kills >= 1, 180),
            ("boss3", "보스 사냥꾼", "지역 보스 3명 처치", self.boss_kills >= 3, 350),
            ("stage5", "대륙 횡단", "지역 5개 클리어", self.cleared_count() >= 5, 500),
            ("pet1", "든든한 동료", "동료를 한 명 얻기", len(self.pets) >= 1, 150),
            ("rescuer", "진짜 영웅", "태현이를 구출", self.game_clear, 1000),
        ]

    def check_achievements(self):
        fresh = []
        for aid, title, desc, complete, reward in self.achievement_data():
            if complete and aid not in self.achievements:
                self.achievements.append(aid)
                self.gold += reward
                fresh.append(title)
        if fresh:
            self.set_message("업적 달성: " + ", ".join(fresh) + "! 보너스 골드 획득", 3.5)

    def teleport_zone(self, idx):
        if not self.zone_available(idx):
            return self.set_message(f"{ZONES[idx]['name']}은(는) 아직 잠겨 있습니다. 앞 지역을 클리어하고 레벨을 올리세요.")
        self.player_x = idx * ZONE_LENGTH + 150
        self.hp = min(self.max_hp, self.hp + int(self.max_hp*.25))
        self.monsters.clear()
        self.active_panel = None
        self.set_message(f"{ZONES[idx]['name']}으로 이동했습니다. HP도 조금 회복했습니다.")

    def continue_dialogue(self):
        self.current_dialogue = None
        self.active_panel = None
        self.save_game()
        self.set_message("다음 모험을 계속하세요. 지도(M)에서 열린 지역을 확인할 수 있습니다.", 3)

    def rebirth(self):
        # 환생은 모든 지역을 클리어한 뒤에만 가능하며, 영구 능력치 보너스를 줍니다.
        if not self.game_clear:
            return self.set_message("최종 보스를 쓰러뜨려야 환생할 수 있습니다.")
        self.rebirth_count += 1
        self.level = 1
        self.exp = 0
        self.gold = 100
        self.attack = 10 + self.rebirth_count * 5
        self.max_hp = 100 + self.rebirth_count * 25
        self.hp = self.max_hp
        self.player_x = 160.0
        self.kills = 0
        self.boss_kills = 0
        self.weapon_level = 0
        self.armor_level = 0
        self.potions = 5
        self.crystals = 0
        self.cleared_zones = [False] * len(ZONES)
        self.checkpoint_zone = 0
        self.skill_points = 0
        self.skill_levels = {"power": 0, "vitality": 0}
        self.claimed_quests = []
        # 업적과 동료는 환생 후에도 유지됩니다.
        self.game_clear = False
        self.root.title("태현이 구하기(?)")
        self.current_dialogue = None
        self.active_panel = None
        self.monsters.clear()
        self.particles.clear()
        self.auto_attack = False
        self.save_game()
        self.set_message(f"환생 {self.rebirth_count}회! 공격력과 최대 HP 보너스를 얻었습니다.", 5)


    # -------------------------- 태현이 키우기 --------------------------
    def gain_taehyun_exp(self, amount):
        self.taehyun_exp += int(amount)
        leveled = False
        while self.taehyun_exp >= self.taehyun_level * 30:
            self.taehyun_exp -= self.taehyun_level * 30
            self.taehyun_level += 1
            leveled = True
        return leveled

    def feed_taehyun(self):
        if not self.game_clear:
            return
        if self.gold < 25:
            self.set_message("밥을 사려면 골드 25개가 필요해요.", 2)
            return
        self.gold -= 25
        self.taehyun_hunger = max(0.0, self.taehyun_hunger - 32)
        self.taehyun_happiness = min(100.0, self.taehyun_happiness + 5)
        self.taehyun_feed_count += 1
        self.save_game()
        self.set_message("태현이에게 밥을 줬어요. 배고픔이 줄었습니다!", 3)

    def play_with_taehyun(self):
        if not self.game_clear:
            return
        self.taehyun_hunger = min(100.0, self.taehyun_hunger + 7)
        self.taehyun_happiness = min(100.0, self.taehyun_happiness + 18)
        leveled = self.gain_taehyun_exp(6)
        self.taehyun_play_count += 1
        self.save_game()
        self.set_message("태현이와 신나게 놀았어요!" + (f" 태현이 Lv.{self.taehyun_level} 성장!" if leveled else ""), 3)

    def train_with_taehyun(self):
        if not self.game_clear:
            return
        self.taehyun_hunger = min(100.0, self.taehyun_hunger + 12)
        self.taehyun_happiness = min(100.0, self.taehyun_happiness + 4)
        leveled = self.gain_taehyun_exp(15)
        self.save_game()
        suffix = f" 태현이가 Lv.{self.taehyun_level}로 성장했어요!" if leveled else " 경험치를 얻었어요."
        self.set_message("태현이와 함께 훈련했어요!" + suffix, 3)

    def update_raising(self, dt):
        # 돌봄 수치는 천천히 변해 게임을 오래 켜 두어도 급격히 나빠지지 않습니다.
        self.taehyun_hunger = min(100.0, self.taehyun_hunger + dt * 0.08)
        self.taehyun_happiness = max(0.0, self.taehyun_happiness - dt * 0.025)

    # -------------------------- 관리자 --------------------------
    def refresh_admin_data(self):
        if not self.api_token or self.role != "admin":
            return False
        try:
            result = api_request("/api/admin/users", token=self.api_token)
            profiles = result.get("users", [])
            self.users = {
                u["username"]: {
                    "nickname": u.get("nickname", u["username"]),
                    "role": u.get("role", "player"),
                    "banned": bool(u.get("banned", False)),
                }
                for u in profiles
            }
            self.admin_saves = {u["username"]: u.get("save", {}) for u in profiles}
            self.admin_targets = sorted(self.users.keys())
            if self.admin_targets:
                self.admin_target_index %= len(self.admin_targets)
            return True
        except RuntimeError as exc:
            self.set_message("관리자 목록을 불러오지 못했습니다: " + str(exc), 5)
            return False

    def toggle_panel(self, panel):
        if panel == "admin" and self.role != "admin":
            return self.set_message("관리자 전용 기능입니다.")
        self.active_panel = None if self.active_panel == panel else panel
        if panel == "admin" and self.active_panel == "admin":
            self.refresh_admin_data()

    def admin_target(self):
        if not self.admin_targets:
            self.refresh_admin_data()
        if not self.admin_targets:
            return None
        self.admin_target_index %= len(self.admin_targets)
        return self.admin_targets[self.admin_target_index]

    def admin_cycle(self, step):
        if self.refresh_admin_data() and self.admin_targets:
            self.admin_target_index = (self.admin_target_index + step) % len(self.admin_targets)

    def admin_get_save(self, name):
        if not name:
            return default_save()
        if name == self.current_user:
            return self.save_payload()
        data = default_save()
        saved = self.admin_saves.get(name, {})
        if isinstance(saved, dict):
            data.update(saved)
        return data

    def admin_write_save(self, name, data):
        if not name or not self.api_token:
            return self.set_message("온라인 관리자 서버에 연결되어 있지 않습니다.")
        try:
            api_request(f"/api/admin/user/{quote(name, safe='')}/save", method="PUT",
                        payload=data, token=self.api_token)
            self.admin_saves[name] = data
            if name == self.current_user:
                self.load_game(name)
                self.active_panel = "admin"
        except RuntimeError as exc:
            self.set_message("관리자 저장 실패: " + str(exc), 5)

    def admin_add_gold(self):
        name = self.admin_target()
        if not name:
            return
        data = self.admin_get_save(name)
        data["gold"] = int(data.get("gold", 0)) + 1000
        self.admin_write_save(name, data)
        self.set_message(f"{name} 계정에 골드 1,000 지급")

    def admin_add_levels(self):
        name = self.admin_target()
        if not name:
            return
        data = self.admin_get_save(name)
        data["level"] = int(data.get("level", 1)) + 5
        data["attack"] = int(data.get("attack", 10)) + 15
        data["max_hp"] = int(data.get("max_hp", 100)) + 60
        data["hp"] = data["max_hp"]
        data["skill_points"] = int(data.get("skill_points", 0)) + 5
        self.admin_write_save(name, data)
        self.set_message(f"{name} 계정 레벨과 능력치 상승")

    def admin_add_items(self):
        name = self.admin_target()
        if not name:
            return
        data = self.admin_get_save(name)
        data["potions"] = int(data.get("potions", 0)) + 10
        data["crystals"] = int(data.get("crystals", 0)) + 5
        self.admin_write_save(name, data)
        self.set_message(f"{name} 계정에 물약 10개와 수정 5개 지급")

    def admin_toggle_ban(self):
        name = self.admin_target()
        if not name or not self.api_token:
            return
        try:
            api_request(f"/api/admin/user/{quote(name, safe='')}/action", method="POST",
                        payload={"action": "toggle_ban"}, token=self.api_token)
            self.refresh_admin_data()
            record = self.users.get(name, {})
            self.set_message(f"{name}: 이용 제한 {'적용' if record.get('banned') else '해제'}")
        except RuntimeError as exc:
            self.set_message("이용 제한 변경 실패: " + str(exc), 5)

    def admin_reset_save(self):
        name = self.admin_target()
        if not name:
            return
        if not messagebox.askyesno("진행 초기화", f"'{name}' 계정의 게임 진행을 초기화할까요?\n계정과 비밀번호는 유지됩니다."):
            return
        self.admin_write_save(name, default_save())
        self.set_message(f"{name} 계정의 진행 상황을 초기화했습니다.")

    def admin_summon_boss(self):
        if self.cleared_zones[self.current_zone_index]:
            return self.set_message("이미 클리어한 지역입니다. 다른 지역으로 이동하세요.")
        self.spawn_zone_boss(self.current_zone_index)

    # -------------------------- 입력 / 게임 업데이트 --------------------------
    def show_game(self):
        self.root.title("태현이 키우기" if self.game_clear else "태현이 구하기(?)")
        self.tick_session += 1
        if self.frame:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg="#8fc9e8")
        self.frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.frame, bg="#8fc9e8", highlightthickness=0, takefocus=True)
        self.canvas.pack(fill="both", expand=True)
        self.root.bind_all("<KeyPress>", self.key_down)
        self.root.bind_all("<KeyRelease>", self.key_up)
        self.canvas.focus_set()
        self.last_tick = time.perf_counter()
        self.tick(self.tick_session)

    def key_down(self, event):
        key = event.keysym.lower()
        if self.current_user is None:
            return
        first = key not in self.keys
        self.keys.add(key)
        if not first:
            return
        if key == "escape":
            if self.active_panel:
                self.active_panel = None
            else:
                self.logout()
            return
        if self.active_panel:
            return
        if key in ("space", "w", "up") and self.on_ground:
            self.jump_v = 430
            self.on_ground = False
        elif key == "j":
            self.attack_nearby()
        elif key == "f":
            self.auto_attack = not self.auto_attack
            self.set_message("자동 공격 켜짐" if self.auto_attack else "자동 공격 꺼짐")
        elif key == "u":
            self.toggle_panel("upgrade")
        elif key == "k":
            self.toggle_panel("shop")
        elif key == "i":
            self.toggle_panel("inventory")
        elif key == "q":
            self.toggle_panel("quests")
        elif key == "m":
            self.toggle_panel("map")
        elif key == "r":
            self.toggle_panel("skills")
        elif key == "t":
            self.toggle_panel("story")
        elif key == "h":
            self.use_potion()
        elif key == "s":
            self.save_game()
            self.set_message("저장 완료!")
        elif key == "f2":
            self.toggle_panel("admin")
        elif key in ("1", "2", "3"):
            self.use_skill(int(key))

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def update_world(self, dt, sw):
        if self.active_panel:
            return
        old_x = self.player_x
        step = 245 * dt
        if "a" in self.keys or "left" in self.keys:
            self.player_x -= step
            self.facing = -1
        if "d" in self.keys or "right" in self.keys:
            self.player_x += step
            self.facing = 1
        self.player_x = max(35, min(WORLD_WIDTH-35, self.player_x))
        old_zone, new_zone = self.zone_index_for(old_x), self.zone_index_for(self.player_x)
        # 지역 입구는 바로 앞 지역 보스를 처치해야 통과할 수 있습니다.
        if new_zone > old_zone:
            if not self.cleared_zones[old_zone]:
                self.player_x = (old_zone+1)*ZONE_LENGTH - 420
                self.spawn_zone_boss(old_zone)
                new_zone = old_zone
            elif self.level < ZONES[new_zone]["need"]:
                self.player_x = new_zone*ZONE_LENGTH - 35
                self.set_message(f"{ZONES[new_zone]['name']} 입장에는 레벨 {ZONES[new_zone]['need']}이 필요합니다.", 2)
                new_zone = old_zone
        zi = self.zone_index_for(self.player_x)
        if not self.cleared_zones[zi] and self.player_x >= (zi+1)*ZONE_LENGTH-420:
            self.player_x = (zi+1)*ZONE_LENGTH-420
            if not any(m.get("zone_boss") for m in self.monsters):
                self.spawn_zone_boss(zi)
        # jump physics, with a stable ground clamp to avoid floating after respawns.
        if not self.on_ground:
            self.jump_height += self.jump_v * dt
            self.jump_v -= 1050 * dt
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jump_v = 0
                self.on_ground = True
        self.monster_timer += dt
        if self.monster_timer >= 1.8 and len(self.monsters) < 5:
            self.monster_timer = 0
            self.spawn_monster(sw)
        for monster in list(self.monsters):
            dx = self.player_x - monster["x"]
            touch_distance = 72 if monster.get("boss") else 37
            if abs(dx) > touch_distance:
                monster["x"] += math.copysign(monster["speed"]*dt, dx)
            monster["flash"] = max(0, monster["flash"] - dt)
            monster["attack_cd"] = max(0.0, monster.get("attack_cd", 0.0)-dt)
            if abs(dx) < (82 if monster.get("boss") else 48) and self.jump_height < 10 and monster["attack_cd"] <= 0:
                raw_damage = int(monster["damage"])
                incoming = max(1, raw_damage-self.total_defense)
                self.hp -= incoming
                monster["attack_cd"] = 1.0 if monster.get("boss") else 1.25
                self.set_message(f"피해 -{incoming} · 물약(H)이나 회복 기운(2)을 사용하세요.", 1.0)
                if self.hp <= 0:
                    self.hp = max(1, int(self.max_hp*.55))
                    self.player_x = self.checkpoint_zone*ZONE_LENGTH + 160
                    self.jump_height = self.jump_v = 0.0
                    self.on_ground = True
                    # 일반 몬스터만 정리하고 보스 진행도는 유지합니다.
                    self.monsters = [m for m in self.monsters if m.get("zone_boss")]
                    self.set_message("잠시 쓰러졌지만 체크포인트에서 다시 일어났습니다. 체력이 회복됐어요.", 3)
                    break
        if self.auto_attack and self.monsters and time.perf_counter()-self.last_attack >= .37:
            if any(abs(m["x"]-self.player_x) < (225 if m.get("boss") else 155) for m in self.monsters):
                self.attack_nearby()
        for p in list(self.particles):
            p["life"] -= dt
            p["rise"] += 34*dt
            if p["life"] <= 0:
                self.particles.remove(p)
        self.check_achievements()

    # -------------------------- 그리기 --------------------------
    def draw_text(self, x, y, text, size=14, color="#f2f4fa", anchor="nw", bold=False):
        self.canvas.create_text(x, y, text=text, fill=color,
            font=("Malgun Gothic", size, "bold" if bold else "normal"), anchor=anchor)

    def click_button(self, x1, y1, x2, y2, label, command, enabled=True, color=None):
        c = self.canvas
        fill = color or ("#345379" if enabled else "#39404a")
        tag = f"btn_{abs(hash((label, round(x1), round(y1), round(x2), round(y2))))%10**10}"
        c.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#6f8eaf", width=1, tags=(tag,))
        c.create_text((x1+x2)/2, (y1+y2)/2, text=label,
            fill="#f5f7fb" if enabled else "#999ea7", font=("Malgun Gothic", 9), tags=(tag,))
        c.tag_bind(tag, "<Button-1>", lambda _e: command() if enabled else None)

    def draw_player(self, sx, ground_y):
        c = self.canvas
        y = ground_y-25-self.jump_height
        c.create_oval(sx-20, ground_y-7, sx+20, ground_y+3, fill="#27313d", outline="")
        leg_color = "#364762"
        c.create_line(sx-7, y+10, sx-10, y+24, fill=leg_color, width=6, capstyle="round")
        c.create_line(sx+7, y+10, sx+10, y+24, fill=leg_color, width=6, capstyle="round")
        c.create_rectangle(sx-14, y-10, sx+14, y+14, fill="#477dc5", outline="#2d5388", width=2)
        c.create_polygon(sx-10, y-2, sx+12, y+1, sx+4, y+7, fill="#f1c35f", outline="")
        c.create_oval(sx-17, y-43, sx+17, y-9, fill="#f0c49c", outline="#9a765e", width=1)
        c.create_arc(sx-19, y-47, sx+19, y-14, start=0, extent=180, fill="#49342f", outline="#49342f", width=4)
        eye = sx+5*self.facing
        c.create_oval(eye-2, y-28, eye+2, y-24, fill="#242a37", outline="")
        c.create_line(sx-4, y-16, sx+5, y-16, fill="#7c443d", width=2)
        if self.facing > 0:
            c.create_line(sx+11, y-1, sx+35, y-25, fill="#d7e3ef", width=5)
            c.create_line(sx+7, y+3, sx+17, y-8, fill="#8a5c3c", width=5)
        else:
            c.create_line(sx-11, y-1, sx-35, y-25, fill="#d7e3ef", width=5)
            c.create_line(sx-7, y+3, sx-17, y-8, fill="#8a5c3c", width=5)
        self.draw_text(sx, y-56, self.nickname, 10, "#fff0bf", "center", True)
        # 동료 펫은 캐릭터 옆을 따라다니는 작은 도형으로 표현합니다.
        for i, pet in enumerate(self.pets):
            px = sx - (38 + i*19)*self.facing
            py = ground_y - 24 - self.jump_height + math.sin(time.perf_counter()*3+i)*4
            pet_color = {"꼬마 슬라임":"#85d98a", "불꽃 여우":"#e58a55", "얼음 정령 친구":"#80d4e8"}.get(pet, "#c8b8e8")
            c.create_oval(px-9, py-17, px+9, py+1, fill=pet_color, outline="#33404d", width=1)
            c.create_oval(px-4, py-10, px-2, py-8, fill="#202b33", outline="")
            c.create_oval(px+3, py-10, px+5, py-8, fill="#202b33", outline="")

    def draw_monster(self, monster, camera_x, gy):
        c = self.canvas
        x = monster["x"]-camera_x
        boss = monster.get("boss", False)
        scale = 1.65 if boss else 1.0
        y = gy-28
        r = 23*scale
        if monster.get("flash", 0) > 0:
            body = "#fff1cb"
        else:
            body = monster["color"]
        c.create_oval(x-r, y+17*scale, x+r, y+27*scale, fill="#27353b", outline="")
        name = monster["name"]
        if "버섯" in name:
            c.create_oval(x-r, y-r*.45, x+r, y+r*.65, fill=body, outline="#3d4750", width=2)
            c.create_oval(x-r*1.1, y-r*.9, x+r*1.1, y+r*.15, fill=body, outline="#3d4750", width=2)
            c.create_oval(x-r*.6, y-r*.7, x-r*.3, y-r*.38, fill="#f6d5bd", outline="")
            c.create_oval(x+r*.15, y-r*.65, x+r*.45, y-r*.33, fill="#f6d5bd", outline="")
        elif "박쥐" in name or "까마귀" in name:
            c.create_polygon(x-r*1.6, y, x-r*.5, y-r*.55, x-r*.25, y+r*.3, x+r*.2, y-r*.5, x+r*1.6, y,
                             x+r*.5, y+r*.55, x-r*.6, y+r*.5, fill=body, outline="#3d4750", width=2)
        elif "유령" in name or "망령" in name or "정령" in name or "불꽃" in name:
            c.create_oval(x-r, y-r, x+r, y+r*.6, fill=body, outline="#3d4750", width=2)
            c.create_polygon(x-r*.8, y+r*.25, x-r*.45, y+r, x, y+r*.4, x+r*.35, y+r, x+r*.8, y+r*.2,
                             fill=body, outline=body)
        elif "골렘" in name or "기사" in name or "왕" in name or "마왕" in name or "경비병" in name:
            c.create_rectangle(x-r*.7, y-r*.65, x+r*.7, y+r*.65, fill=body, outline="#343b4a", width=3)
            c.create_polygon(x-r*.65, y-r*.55, x-r*.95, y-r*1.0, x-r*.25, y-r*.7, fill=body, outline="#343b4a")
            c.create_polygon(x+r*.65, y-r*.55, x+r*.95, y-r*1.0, x+r*.25, y-r*.7, fill=body, outline="#343b4a")
        else:
            c.create_oval(x-r, y-r*.6, x+r, y+r*.65, fill=body, outline="#3d4750", width=2)
            if boss:
                c.create_polygon(x-r*.8,y-r*.3,x-r*1.25,y-r*1.0,x-r*.2,y-r*.55,fill=body,outline="#3d4750")
                c.create_polygon(x+r*.8,y-r*.3,x+r*1.25,y-r*1.0,x+r*.2,y-r*.55,fill=body,outline="#3d4750")
        eye_r = 4 if boss else 3
        c.create_oval(x-r*.38-eye_r, y-r*.15-eye_r, x-r*.38+eye_r, y-r*.15+eye_r, fill="#fff5d8", outline="")
        c.create_oval(x+r*.38-eye_r, y-r*.15-eye_r, x+r*.38+eye_r, y-r*.15+eye_r, fill="#fff5d8", outline="")
        c.create_oval(x-r*.38-1, y-r*.15-1, x-r*.38+2, y-r*.15+2, fill="#242631", outline="")
        c.create_oval(x+r*.38-1, y-r*.15-1, x+r*.38+2, y-r*.15+2, fill="#242631", outline="")
        bw = 68 if boss else 50
        by = y-r-31
        c.create_rectangle(x-bw/2, by, x+bw/2, by+7, fill="#353947", outline="#1b2430")
        fillw = bw*max(0, min(1, monster["hp"]/max(1, monster["max_hp"])))
        c.create_rectangle(x-bw/2+1, by+1, x-bw/2+1+fillw, by+6, fill="#e05d65", outline="")
        self.draw_text(x, by-7, name, 9 if not boss else 11, "#fff0d3", "center", boss)

    def draw_zone_decor(self, c, zone, camera_x, gy, sw, zi):
        for wx in range(zi*ZONE_LENGTH+130, (zi+1)*ZONE_LENGTH-80, 250):
            sx = wx-camera_x
            if not (-110 < sx < sw+110):
                continue
            kind = zone["decor"]
            if kind == "tree":
                c.create_rectangle(sx-6,gy-75,sx+6,gy,fill="#6e5037",outline="")
                c.create_oval(sx-36,gy-128,sx+36,gy-55,fill="#3d8a55",outline="")
                c.create_oval(sx-47,gy-98,sx+1,gy-47,fill="#4a9b61",outline="")
            elif kind == "mushroom":
                c.create_rectangle(sx-5,gy-45,sx+5,gy,fill="#e5d9bd",outline="")
                c.create_arc(sx-23,gy-69,sx+23,gy-27,start=0,extent=180,fill="#cb6c61",outline="#884e4b",width=2)
                c.create_oval(sx-9,gy-58,sx-3,gy-52,fill="#f6e5c4",outline="")
                c.create_oval(sx+5,gy-64,sx+11,gy-58,fill="#f6e5c4",outline="")
            elif kind == "mine":
                c.create_polygon(sx-36,gy,sx-23,gy-72,sx+23,gy-72,sx+36,gy,fill="#5c5969",outline="#434758",width=3)
                c.create_rectangle(sx-17,gy-41,sx+17,gy,fill="#222735",outline="#a4a9b5",width=2)
                c.create_oval(sx-4,gy-64,sx+4,gy-56,fill="#b5d7de",outline="")
            elif kind == "lava":
                c.create_polygon(sx-35,gy,sx-18,gy-62,sx-2,gy-30,sx+17,gy-91,sx+38,gy,fill="#774c43",outline="#ae6550",width=2)
                c.create_line(sx-20,gy-8,sx-9,gy-27,sx+3,gy-12,sx+18,gy-47,fill="#f59b47",width=3)
            elif kind == "ice":
                c.create_polygon(sx-28,gy,sx-18,gy-65,sx-4,gy-43,sx+5,gy-100,sx+26,gy,fill="#a2d8e9",outline="#d7f3f9",width=2)
                c.create_line(sx+5,gy-88,sx+13,gy-42,fill="#e7fbff",width=3)
            elif kind == "castle":
                c.create_rectangle(sx-30,gy-80,sx+30,gy,fill="#34364d",outline="#696585",width=2)
                for dx in (-25,-5,15):
                    c.create_rectangle(sx+dx,gy-95,sx+dx+10,gy-78,fill="#34364d",outline="#696585")
                c.create_rectangle(sx-8,gy-38,sx+8,gy,fill="#181b2b",outline="")
            elif kind == "cliff":
                c.create_polygon(sx-48,gy,sx-25,gy-82,sx-3,gy-33,sx+19,gy-104,sx+48,gy,fill="#748f9f",outline="#d1e5e8",width=2)
                c.create_line(sx-20,gy-17,sx-3,gy-42,sx+7,gy-23,fill="#d7ebef",width=3)
            elif kind == "ruin":
                c.create_rectangle(sx-34,gy-70,sx-18,gy,fill="#91876f",outline="#4e514c",width=2)
                c.create_rectangle(sx+15,gy-85,sx+31,gy,fill="#91876f",outline="#4e514c",width=2)
                c.create_line(sx-45,gy-71,sx+41,gy-71,fill="#c3b694",width=7)
                c.create_polygon(sx-42,gy-70,sx,gy-103,sx+42,gy-70,fill="#8e866f",outline="#4e514c",width=2)
            elif kind == "beach":
                c.create_line(sx-45,gy-15,sx-22,gy-22,sx,gy-15,sx+24,gy-22,sx+45,gy-15,fill="#d6eaf0",width=3)
                c.create_oval(sx-18,gy-50,sx+18,gy-14,fill="#d3a56e",outline="#855e49",width=2)
                c.create_line(sx,gy-48,sx,gy-17,fill="#855e49",width=2)
                c.create_line(sx-16,gy-32,sx+16,gy-32,fill="#855e49",width=2)
            elif kind == "cloud":
                c.create_oval(sx-42,gy-93,sx+15,gy-48,fill="#eef6ff",outline="#96b7db",width=2)
                c.create_oval(sx-15,gy-115,sx+35,gy-56,fill="#eef6ff",outline="#96b7db",width=2)
                c.create_oval(sx+8,gy-91,sx+53,gy-49,fill="#eef6ff",outline="#96b7db",width=2)
                c.create_line(sx+4,gy-48,sx+4,gy-5,fill="#a9c6e1",width=3)
            elif kind == "swamp":
                c.create_rectangle(sx-7,gy-72,sx+7,gy,fill="#4b5a40",outline="")
                c.create_oval(sx-43,gy-102,sx+43,gy-47,fill="#526e55",outline="#334c3c",width=2)
                c.create_oval(sx-28,gy-62,sx+29,gy-30,fill="#7d9867",outline="#526e55",width=2)
                c.create_oval(sx-35,gy-8,sx+35,gy+5,fill="#66784a",outline="")
            elif kind == "crystal":
                c.create_polygon(sx-35,gy,sx-18,gy-66,sx-4,gy-39,sx+7,gy-111,sx+25,gy-51,sx+37,gy,fill="#8b91e3",outline="#d8d9ff",width=2)
                c.create_polygon(sx-8,gy,sx+2,gy-51,sx+15,gy-22,sx+27,gy,fill="#72d2e2",outline="#d8f8ff",width=2)
            else:
                c.create_rectangle(sx-28,gy-87,sx+28,gy,fill="#302e3b",outline="#65566c",width=2)
                c.create_rectangle(sx-10,gy-54,sx+10,gy,fill="#171721",outline="#846377")
                c.create_polygon(sx-32,gy-87,sx-19,gy-112,sx-5,gy-87,fill="#302e3b",outline="#65566c")
                c.create_polygon(sx+5,gy-87,sx+19,gy-112,sx+32,gy-87,fill="#302e3b",outline="#65566c")

    def draw_game(self):
        if self.game_clear:
            self.draw_raising_game()
            return
        c = self.canvas
        c.delete("all")
        sw, sh = max(1,c.winfo_width()), max(1,c.winfo_height())
        zi = self.current_zone_index
        zone = ZONES[zi]
        # Camera tracks the player on every frame, not just when entering a new area.
        camera_x = max(0, min(self.player_x-sw*.42, WORLD_WIDTH-sw))
        c.configure(bg=zone["sky"])
        c.create_rectangle(0,0,sw,sh,fill=zone["sky"],outline="")
        # parallax hills and drifting clouds
        hill_offset = (camera_x*.22) % 280
        for i in range(-1, sw//280+3):
            hx = i*280-hill_offset
            c.create_oval(hx-60,205,hx+270,440,fill=zone["hill"],outline="")
            c.create_oval(hx+75,245,hx+365,455,fill=zone["hill"],outline="")
        cloud_offset = (camera_x*.09) % 255
        cloud_color = "#e8f3f6" if zi < 5 else "#9491ad"
        for i in range(-1, sw//255+3):
            cx = i*255-cloud_offset
            c.create_oval(cx,72+(i%3)*24,cx+74,99+(i%3)*24,fill=cloud_color,outline="")
            c.create_oval(cx+23,56+(i%3)*24,cx+91,96+(i%3)*24,fill=cloud_color,outline="")
        gy = sh-92
        c.create_rectangle(0,gy,sw,sh,fill=zone["ground"],outline="")
        c.create_rectangle(0,gy,sw,gy+14,fill=zone["hill"],outline="")
        for i in range(-1,sw//75+3):
            gx = i*75-int(camera_x)%75
            c.create_line(gx,gy,gx+31,gy+12,fill=zone["hill"],width=3)
        self.draw_zone_decor(c,zone,camera_x,gy,sw,zi)
        # 지역별 문/포털. 보스 처치 전에는 닫혀 있습니다.
        gate_x = (zi+1)*ZONE_LENGTH-75-camera_x
        if -60 < gate_x < sw+60:
            gate_color = "#75d59e" if self.cleared_zones[zi] else "#db6575"
            c.create_rectangle(gate_x-28,gy-110,gate_x+28,gy,fill="#2c3447",outline=gate_color,width=3)
            c.create_oval(gate_x-19,gy-98,gate_x+19,gy-60,fill=gate_color,outline="#f7e3bd",width=2)
            c.create_rectangle(gate_x-10,gy-49,gate_x+10,gy,fill="#121925",outline="")
            status = "열림" if self.cleared_zones[zi] else "보스 격파 필요"
            self.draw_text(gate_x,gy-131,status,9,gate_color,"center",True)
        for monster in self.monsters:
            if -130 < monster["x"]-camera_x < sw+130:
                self.draw_monster(monster,camera_x,gy)
        self.draw_player(self.player_x-camera_x,gy)
        # Top-left status and main objective
        c.create_rectangle(12,12,330,137,fill="#17202d",outline="#536a86",width=2)
        badge = "  [관리자]" if self.role == "admin" else ""
        self.draw_text(25,20,f"{self.nickname} · Lv.{self.level}{badge}",13,"#ffe18f",bold=True)
        self.draw_text(25,47,f"EXP {self.exp}/{self.level*30}",10)
        c.create_rectangle(100,50,306,61,fill="#333c4a",outline="")
        c.create_rectangle(100,50,100+206*min(1,self.exp/max(1,self.level*30)),61,fill="#68bf7a",outline="")
        self.draw_text(25,70,f"HP {self.hp}/{self.max_hp}",10)
        c.create_rectangle(100,73,306,84,fill="#333c4a",outline="")
        c.create_rectangle(100,73,100+206*max(0,min(1,self.hp/max(1,self.max_hp))),84,fill="#da535b",outline="")
        self.draw_text(25,95,f"공격 {self.total_attack} · 방어 {self.total_defense}",10,"#c9d8e8")
        self.draw_text(25,115,f"스킬 포인트 {self.skill_points}",9,"#c9d8e8")
        # top right inventory summary
        c.create_rectangle(sw-235,12,sw-12,118,fill="#17202d",outline="#536a86",width=2)
        self.draw_text(sw-220,22,f"골드 {self.gold:,}",13,"#ffe080",bold=True)
        self.draw_text(sw-220,47,f"처치 {self.kills} · 보스 {self.boss_kills}",10)
        self.draw_text(sw-220,65,f"무기 +{self.weapon_level} · 방어구 +{self.armor_level}",9)
        self.draw_text(sw-220,82,f"물약 {self.potions} · 수정 {self.crystals}",9,"#b9dfe9")
        self.draw_text(sw-220,99,f"동료 {len(self.pets)}명",9,"#c9d8e8")
        # stage progress and story objective
        self.draw_text(sw/2,18,f"STAGE {zi+1}/{len(ZONES)}  ·  {zone['name']}  ·  환생 {self.rebirth_count}회",15,"#fff3d2","center",True)
        cleared = self.cleared_count()
        if self.game_clear:
            objective = "최종 목표 완료: 태현이 구출 성공!"
        elif self.cleared_zones[zi]:
            objective = "지역 클리어! 다음 지역으로 이동하세요."
        else:
            objective = f"목표: {zone['boss'][0]}을(를) 쓰러뜨리고 다음 길을 열기"
        self.draw_text(sw/2,43,objective,10,"#1d2d3d","center",True)
        self.draw_text(sw/2,62,f"캠페인 진행 {cleared}/{len(ZONES)} 지역 클리어",9,"#213447","center")
        # Bottom desktop controls. PC has keyboard/mouse controls; no mobile touch pad is shown.
        labels = [
            ("성장(U)",lambda:self.toggle_panel("upgrade")), ("상점(K)",lambda:self.toggle_panel("shop")),
            ("가방(I)",lambda:self.toggle_panel("inventory")), ("임무(Q)",lambda:self.toggle_panel("quests")),
            ("스킬(R)",lambda:self.toggle_panel("skills")), ("지도(M)",lambda:self.toggle_panel("map")),
            ("물약(H)",self.use_potion), ("이야기(T)",lambda:self.toggle_panel("story")),
            ("저장(S)",lambda:(self.save_game(),self.set_message("저장 완료!"))), ("로그아웃",self.logout),
        ]
        if self.role == "admin":
            labels.insert(-1,("관리자(F2)",lambda:self.toggle_panel("admin")))
        by1,by2 = sh-48,sh-14
        c.create_rectangle(10,by1-5,sw-10,by2+5,fill="#17202d",outline="#536a86")
        gap = 4
        bw = min(104,max(48,(sw-28-gap*(len(labels)-1))/len(labels)))
        total = bw*len(labels)+gap*(len(labels)-1)
        sx = (sw-total)/2
        for i,(label,command) in enumerate(labels):
            bx = sx+i*(bw+gap)
            self.click_button(bx,by1,bx+bw,by2,label,command)
        if time.time() < self.message_until and self.message:
            c.create_rectangle(sw/2-250,sh-100,sw/2+250,sh-65,fill="#253044",outline="#e1bf68",width=2)
            self.draw_text(sw/2,sh-82,self.message,9,"#ffe597","center")
        for p in self.particles:
            self.draw_text(p["x"]-camera_x,gy-85-p["rise"],p["text"],10,"#ffdf86","center",True)
        if self.active_panel:
            self.draw_overlay(sw,sh)


    def draw_raising_game(self):
        c = self.canvas
        c.delete("all")
        sw, sh = max(1, c.winfo_width()), max(1, c.winfo_height())
        c.configure(bg="#bfe0ee")
        gy = int(sh * 0.70)

        # 단순한 도형과 적은 오브젝트로 꾸민 돌봄 화면입니다.
        c.create_rectangle(0, 0, sw, sh, fill="#bfe0ee", outline="")
        c.create_oval(-sw*.12, gy-100, sw*.43, gy+80, fill="#9dcfae", outline="")
        c.create_oval(sw*.34, gy-120, sw*1.12, gy+80, fill="#86bd9b", outline="")
        c.create_rectangle(0, gy, sw, sh, fill="#72a96e", outline="")
        c.create_rectangle(0, gy, sw, gy+13, fill="#9ccb80", outline="")

        house_x = sw - 130
        c.create_rectangle(house_x-58, gy-100, house_x+58, gy, fill="#f0d3a1", outline="#765943", width=2)
        c.create_polygon(house_x-72, gy-98, house_x, gy-158, house_x+72, gy-98,
                         fill="#bc765b", outline="#765943", width=2)
        c.create_rectangle(house_x-13, gy-49, house_x+13, gy, fill="#7b6658", outline="#604b3e")
        c.create_rectangle(58, gy-66, 72, gy, fill="#886244", outline="")
        c.create_oval(27, gy-126, 103, gy-51, fill="#4e9465", outline="#39754e", width=2)
        c.create_oval(45, gy-147, 111, gy-85, fill="#68a96d", outline="#39754e", width=2)

        self.draw_text(sw/2, 17, "태현이 키우기", 23, "#26445b", "center", True)
        self.draw_text(sw/2, 49, "드디어 구출했어요! 이제 밥도 주고, 놀고, 함께 성장해 봐요.", 10, "#38576b", "center")

        c.create_rectangle(16, 78, 254, 219, fill="#f5f3e9", outline="#7897a2", width=2)
        self.draw_text(30, 88, "태현이의 오늘", 12, "#304b5a", bold=True)
        self.draw_text(30, 119, f"배고픔 {int(self.taehyun_hunger)} / 100", 9, "#304b5a")
        c.create_rectangle(30, 139, 235, 150, fill="#d8d8cf", outline="")
        c.create_rectangle(30, 139, 30+205*self.taehyun_hunger/100, 150, fill="#d88158", outline="")
        self.draw_text(30, 160, f"기분 {int(self.taehyun_happiness)} / 100", 9, "#304b5a")
        c.create_rectangle(30, 180, 235, 191, fill="#d8d8cf", outline="")
        c.create_rectangle(30, 180, 30+205*self.taehyun_happiness/100, 191, fill="#6bb982", outline="")
        self.draw_text(30, 199, f"보유 골드 {self.gold:,} G", 9, "#8a6635", bold=True)

        c.create_rectangle(sw-250, 78, sw-16, 186, fill="#f5f3e9", outline="#7897a2", width=2)
        self.draw_text(sw-234, 88, "함께한 시간", 12, "#304b5a", bold=True)
        self.draw_text(sw-234, 119, f"태현이 Lv.{self.taehyun_level}", 13, "#5b7392", bold=True)
        self.draw_text(sw-234, 144, f"EXP {self.taehyun_exp} / {self.taehyun_level*30}", 9, "#304b5a")
        c.create_rectangle(sw-234, 161, sw-32, 171, fill="#d8d8cf", outline="")
        c.create_rectangle(sw-234, 161, sw-234+202*min(1,self.taehyun_exp/max(1,self.taehyun_level*30)), 171,
                           fill="#76a9d5", outline="")

        scale = min(1.35, 0.82 + self.taehyun_level * 0.035)
        px, py = sw * 0.50, gy
        r = 28 * scale
        c.create_oval(px-r*1.35, py-2, px+r*1.35, py+10, fill="#4d805d", outline="")
        c.create_line(px-11*scale, py-28*scale, px-14*scale, py-2, fill="#526c8d", width=max(3,int(6*scale)))
        c.create_line(px+11*scale, py-28*scale, px+14*scale, py-2, fill="#526c8d", width=max(3,int(6*scale)))
        c.create_rectangle(px-25*scale, py-68*scale, px+25*scale, py-24*scale,
                           fill="#8e9ec6", outline="#536b91", width=2)
        c.create_oval(px-31*scale, py-126*scale, px+31*scale, py-64*scale,
                      fill="#f2c9a6", outline="#a47a61", width=2)
        c.create_arc(px-33*scale, py-132*scale, px+33*scale, py-75*scale,
                     start=0, extent=180, fill="#49352f", outline="#49352f", width=max(3,int(5*scale)))
        c.create_oval(px-13*scale, py-101*scale, px-7*scale, py-94*scale, fill="#29333d", outline="")
        c.create_oval(px+7*scale, py-101*scale, px+13*scale, py-94*scale, fill="#29333d", outline="")
        c.create_arc(px-9*scale, py-96*scale, px+10*scale, py-80*scale,
                     start=200, extent=140, style="arc", outline="#9b5d52", width=2)
        self.draw_text(px, py-154*scale, "태현", 12, "#fff3cf", "center", True)
        if self.taehyun_happiness >= 80:
            self.draw_text(px+55*scale, py-112*scale, "♪", 20, "#fff2a8", "center", True)
        elif self.taehyun_hunger >= 80:
            self.draw_text(px+55*scale, py-112*scale, "배고파!", 9, "#7d4c40", "center", True)

        actions = [
            ("밥 주기 · 25G", self.feed_taehyun, self.gold >= 25),
            ("놀아주기", self.play_with_taehyun, True),
            ("함께 훈련", self.train_with_taehyun, True),
            ("환생해서 모험", self.rebirth, True),
            ("로그아웃", self.logout, True),
        ]
        gap = 8
        bw = min(146, max(88, (sw-36-gap*(len(actions)-1))/len(actions)))
        total = bw*len(actions) + gap*(len(actions)-1)
        start_x = (sw-total)/2
        by1, by2 = sh-65, sh-25
        for i, (label, command, enabled) in enumerate(actions):
            bx = start_x + i*(bw+gap)
            self.click_button(bx, by1, bx+bw, by2, label, command, enabled)
        if time.time() < self.message_until and self.message:
            self.draw_text(sw/2, sh-88, self.message, 10, "#fff7d5", "center", True)

    def draw_overlay(self, sw, sh):
        c = self.canvas
        panel = self.active_panel
        if panel == "dialogue":
            data = self.current_dialogue or {"name":"모험가", "line":"태현이는 여기에 없어요. 일단 이거 받으세요.", "reward":"보상을 받았습니다."}
            c.create_rectangle(0,0,sw,sh,fill="#0c1018",stipple="gray50",outline="")
            x1,y1,x2,y2 = sw/2-285,sh/2-145,sw/2+285,sh/2+145
            c.create_rectangle(x1,y1,x2,y2,fill="#202b3b",outline="#e7c36e",width=3)
            # 간단한 도형 캐릭터와 이름표를 표시해 NPC가 실제로 등장한 느낌을 줍니다.
            c.create_oval(sw/2-34,y1+20,sw/2+34,y1+88,fill="#f0c49c",outline="#9a765e",width=2)
            c.create_arc(sw/2-37,y1+15,sw/2+37,y1+60,start=0,extent=180,fill="#49342f",outline="#49342f",width=5)
            c.create_rectangle(sw/2-27,y1+77,sw/2+27,y1+120,fill="#5c83b4",outline="#304e75",width=2)
            self.draw_text(sw/2,y1+7,data.get("name","모험가"),12,"#ffe18f","center",True)
            self.draw_text(sw/2,y1+143,data.get("line","태현이는 여기에 없어요. 일단 이거 받으세요."),13,"#f2f4fa","center",True)
            self.draw_text(sw/2,y2-39,data.get("reward","보상을 받았습니다."),9,"#a7e7bf","center")
            self.click_button(sw/2-83,y2-2,sw/2+83,y2+30,"보상 받고 계속",self.continue_dialogue)
            return
        if panel == "ending":
            data = self.current_dialogue or {"name":"태현", "line":f"고마워요 {self.nickname}, 환생할 기회를 줄게요.", "reward":"태현이를 구출했습니다!"}
            x1,y1,x2,y2 = sw/2-270,sh/2-190,sw/2+270,sh/2+190
            c.create_rectangle(0,0,sw,sh,fill="#0c1018",stipple="gray50",outline="")
            c.create_rectangle(x1,y1,x2,y2,fill="#202b3b",outline="#e7c36e",width=3)
            self.draw_text(sw/2,y1+24,"FINAL MISSION COMPLETE",13,"#a7e7bf","center",True)
            # 최종 보스 뒤에만 '태현' 이름표가 붙은 인물이 등장합니다.
            c.create_oval(sw/2-34,y1+42,sw/2+34,y1+110,fill="#f0c49c",outline="#9a765e",width=2)
            c.create_arc(sw/2-37,y1+37,sw/2+37,y1+82,start=0,extent=180,fill="#49342f",outline="#49342f",width=5)
            c.create_rectangle(sw/2-27,y1+99,sw/2+27,y1+139,fill="#d6c5e6",outline="#79628f",width=2)
            self.draw_text(sw/2,y1+37,"태현",12,"#ffe18f","center",True)
            self.draw_text(sw/2,y1+157,data.get("line",f"고마워요 {self.nickname}, 환생할 기회를 줄게요."),13,"#fff0c0","center",True)
            self.draw_text(sw/2,y1+184,"모든 지역 클리어 · 태현이 구출 성공!",9,"#d7e4f3","center")
            self.draw_text(sw/2,y1+208,f"최종 레벨 {self.level} · 몬스터 {self.kills}마리 · 환생 {self.rebirth_count}회",9,"#b9cce0","center")
            self.click_button(sw/2-205,y2-42,sw/2-15,y2-8,"환생 기회 받기",self.rebirth)
            self.click_button(sw/2+15,y2-42,sw/2+205,y2-8,"계속하기",lambda:setattr(self,"active_panel",None))
            return
        c.create_rectangle(0,0,sw,sh,fill="#0c1018",stipple="gray50",outline="",tags=("overlay_bg",))
        c.tag_bind("overlay_bg","<Button-1>",lambda _e:"break")
        x1,y1,x2,y2 = sw/2-250,sh/2-235,sw/2+250,sh/2+235
        c.create_rectangle(x1,y1,x2,y2,fill="#18202f",outline="#e1bf68",width=2)
        titles = {"upgrade":"성장과 장비 강화","shop":"여행 상점","inventory":"가방 · 동료 · 업적",
                  "quests":"모험 임무","map":"월드 지도","skills":"스킬과 훈련",
                  "story":"태현이 구출 작전","admin":"관리자 도구"}
        self.draw_text(sw/2,y1+25,titles.get(panel,"메뉴"),19,"#ffe18f","center",True)
        if panel == "upgrade":
            self.draw_text(sw/2,y1+56,f"골드 {self.gold:,} · 공격 {self.total_attack} · 방어 {self.total_defense}",11,anchor="center")
            self.draw_text(x1+120,y1+86,f"기본 공격력 +5 / {self.level*30}G",10,anchor="center")
            self.click_button(x1+28,y1+100,x1+212,y1+136,"기본 공격력 강화",self.upgrade_attack,self.gold>=self.level*30)
            self.draw_text(x1+120,y1+158,f"최대 HP +25 / {self.level*25}G",10,anchor="center")
            self.click_button(x1+28,y1+172,x1+212,y1+208,"최대 체력 강화",self.upgrade_hp,self.gold>=self.level*25)
            wc,ac = 80+self.weapon_level*95,70+self.armor_level*85
            self.draw_text(x1+375,y1+86,f"무기 +1 / {wc}G",10,anchor="center")
            self.click_button(x1+278,y1+100,x1+462,y1+136,"무기 강화",self.upgrade_weapon,self.gold>=wc)
            self.draw_text(x1+375,y1+158,f"방어구 +1 / {ac}G",10,anchor="center")
            self.click_button(x1+278,y1+172,x1+462,y1+208,"방어구 강화",self.upgrade_armor,self.gold>=ac)
            self.draw_text(sw/2,y1+238,"강화 수정이 있으면 장비 강화가 2단계씩 올라갑니다.",9,"#b8c8da","center")
        elif panel == "shop":
            self.draw_text(sw/2,y1+60,f"보유 골드: {self.gold:,}",12,"#ffe080","center")
            for label,desc,btn,cost,fn in [
                ("회복 물약","전투 중 HP 회복","물약 구매",25,lambda:self.buy_item("potion")),
                ("강화 수정","무기/방어구 강화 보조","수정 구매",115,lambda:self.buy_item("crystal")),
                ("공격 주문서","기본 공격력 +10","주문서 사용",175,lambda:self.buy_item("scroll")),
            ]:
                idx = ["회복 물약","강화 수정","공격 주문서"].index(label)
                yy = y1+93+idx*83
                c.create_rectangle(x1+22,yy,x2-22,yy+70,fill="#222e40",outline="#425772")
                self.draw_text(x1+38,yy+12,label,12,"#ffe18f",bold=True)
                self.draw_text(x1+38,yy+38,f"{desc} · {cost}G",9,"#b8c8da")
                self.click_button(x2-155,yy+17,x2-38,yy+54,btn,fn,self.gold>=cost)
        elif panel == "inventory":
            self.draw_text(x1+28,y1+62,f"회복 물약: {self.potions}개",12)
            self.draw_text(x1+28,y1+91,f"강화 수정: {self.crystals}개",12,"#a3e1ef")
            self.draw_text(x1+28,y1+120,f"무기 강화: +{self.weapon_level} · 방어구 강화: +{self.armor_level}",10)
            self.draw_text(x1+28,y1+149,f"동료: {', '.join(self.pets) if self.pets else '아직 동료가 없습니다'}",10,"#b5e8bf")
            self.draw_text(x1+28,y1+179,f"업적 {len(self.achievements)}/{len(self.achievement_data())} 달성",10,"#ffe18f")
            yy = y1+211
            for aid,title,desc,complete,reward in self.achievement_data():
                state = "완료" if aid in self.achievements else ("달성 가능" if complete else "진행 중")
                self.draw_text(x1+32,yy,f"{'★' if aid in self.achievements else '☆'} {title} — {state}",9,"#bfe0c4" if aid in self.achievements else "#d4ddeb")
                yy += 23
            self.click_button(x1+27,y2-50,x1+215,y2-15,"물약 사용 (H)",self.use_potion,self.potions>0 and self.hp<self.max_hp)
        elif panel == "quests":
            qs = self.quest_data()
            row_h = 43
            for i,q in enumerate(qs):
                yy = y1+55+i*row_h
                if yy+row_h > y2-40:
                    break
                c.create_rectangle(x1+16,yy,x2-16,yy+38,fill="#222e40",outline="#425772")
                state = q["id"] in self.claimed_quests
                self.draw_text(x1+27,yy+6,q["name"],10,"#ffe18f" if not state else "#91d8a5",bold=True)
                self.draw_text(x1+27,yy+23,f"{q['desc']} ({q['progress']}/{q['goal']})",8,"#c7d5e5")
                self.click_button(x2-112,yy+5,x2-25,yy+33,"완료" if state else f"+{q['gold']}G",
                                  lambda qid=q["id"]:self.claim_quest(qid),not state and q["progress"]>=q["goal"])
        elif panel == "map":
            row_h = 29
            for i,z in enumerate(ZONES):
                yy = y1+47+i*row_h
                unlocked = self.zone_available(i)
                current = i == self.current_zone_index
                cleared = self.cleared_zones[i]
                c.create_rectangle(x1+17,yy,x2-17,yy+25,fill="#293b4d" if current else "#222e40",outline="#425772")
                status = "클리어" if cleared else ("현재 지역" if current else ("입장 가능" if unlocked else f"Lv.{z['need']} / 이전 보스 필요"))
                self.draw_text(x1+27,yy+4,f"{i+1}. {z['name']}",9,"#ffe18f" if current else "#eef3fa",bold=current)
                self.draw_text(x1+190,yy+5,status,8,"#a6d9b3" if cleared else "#b8c8da")
                self.click_button(x2-92,yy+2,x2-25,yy+23,"이동",lambda idx=i:self.teleport_zone(idx),unlocked)
        elif panel == "skills":
            self.draw_text(sw/2,y1+57,f"남은 스킬 포인트: {self.skill_points}",12,"#ffe18f","center")
            self.draw_text(x1+28,y1+88,"활성 스킬 (전투 중 단축키 사용)",11,"#b9dfe9",bold=True)
            self.draw_text(x1+34,y1+117,"[1] 번개 베기 — 공격력의 2.2배, 재사용 3.5초",9)
            self.draw_text(x1+34,y1+141,"[2] 회복 기운 — 레벨 3부터, 체력 회복, 재사용 10초",9)
            self.draw_text(x1+34,y1+165,"[3] 폭풍 일격 — 레벨 7부터, 주변 적 공격, 재사용 8초",9)
            self.draw_text(x1+28,y1+205,"패시브 훈련 (레벨업으로 포인트 획득)",11,"#b9dfe9",bold=True)
            self.draw_text(x1+122,y1+238,f"검술 훈련 Lv.{self.skill_levels['power']} · 공격 +3",9,anchor="center")
            self.click_button(x1+28,y1+253,x1+215,y1+291,"검술 훈련 +1",lambda:self.buy_passive("power"),self.skill_points>0)
            self.draw_text(x1+375,y1+238,f"튼튼한 체력 Lv.{self.skill_levels['vitality']} · HP +30",9,anchor="center")
            self.click_button(x1+278,y1+253,x1+462,y1+291,"체력 훈련 +1",lambda:self.buy_passive("vitality"),self.skill_points>0)
            self.draw_text(sw/2,y1+326,"자동 공격 F · 점프 Space · 공격 J",9,"#b8c8da","center")
        elif panel == "story":
            story = [
                "[작전 개요] 태현이가 정체불명의 마왕에게 납치되었다!",
                "총 13개 지역의 수호 보스를 차례로 쓰러뜨려야 한다.",
                "첫 12명의 보스를 이기면 다른 인물이 나타나 아이템을 준다.",
                "마지막 13번째 지역에서 감금의 마왕을 이기면 태현이를 만날 수 있다.",
                "태현이는 환생의 기회를 주며, 환생하면 영구 능력치 보너스를 얻는다.",
            ]
            yy = y1+51
            for line in story:
                self.draw_text(x1+25,yy,line,9,"#dbe5f2")
                yy += 22
            self.draw_text(x1+25,y1+166,"현재 보고",10,"#ffe18f",bold=True)
            yy = y1+187
            for i,z in enumerate(ZONES):
                status = "보스 격파" if self.cleared_zones[i] else ("진행 중" if i==self.current_zone_index else "미확인")
                self.draw_text(x1+28,yy,f"{i+1}. {z['name']} — {status}",8,"#a8dbb5" if self.cleared_zones[i] else "#dbe5f2")
                yy += 17
            if self.game_clear:
                self.draw_text(sw/2,y2-27,"작전 성공! 태현이는 안전하게 구출되었습니다.",9,"#9ae0ab","center",True)
        elif panel == "admin":
            target = self.admin_target()
            record = self.users.get(target, {}) if target else {}
            data = self.admin_get_save(target) if target else default_save()
            status = "이용 제한" if record.get("banned") else "정상"
            self.draw_text(sw/2,y1+52,f"대상 계정: {target or '없음'} · 상태: {status}",11,"#fff0c8","center")
            self.click_button(x1+25,y1+66,x1+85,y1+99,"◀",lambda:self.admin_cycle(-1))
            self.click_button(x2-85,y1+66,x2-25,y1+99,"▶",lambda:self.admin_cycle(1))
            self.draw_text(sw/2,y1+117,f"Lv.{data.get('level',1)} · 골드 {data.get('gold',0):,} · 처치 {data.get('kills',0)}",10,anchor="center")
            self.click_button(x1+25,y1+135,x1+215,y1+172,"골드 +1,000",self.admin_add_gold)
            self.click_button(x1+278,y1+135,x1+468,y1+172,"레벨 +5",self.admin_add_levels)
            self.click_button(x1+25,y1+183,x1+215,y1+220,"물약 10 + 수정 5",self.admin_add_items)
            self.click_button(x1+278,y1+183,x1+468,y1+220,"현재 지역 보스 소환",self.admin_summon_boss)
            banned = record.get("banned",False)
            self.click_button(x1+25,y1+231,x1+215,y1+268,"이용 제한 해제" if banned else "계정 이용 제한",self.admin_toggle_ban,target!="연욱","#7f4146" if target!="연욱" else None)
            self.click_button(x1+278,y1+231,x1+468,y1+268,"진행 초기화",self.admin_reset_save)
            self.draw_text(sw/2,y2-26,"전체 계정을 온라인 서버에서 관리합니다.",9,"#b8c8da","center")
        self.click_button(sw/2-58,y2+8,sw/2+58,y2+38,"닫기 (ESC)",lambda:setattr(self,"active_panel",None))

    def tick(self, session):
        if session != self.tick_session:
            return
        if not self.canvas or not self.canvas.winfo_exists():
            return
        now = time.perf_counter()
        dt = min(.04,max(0.0,now-self.last_tick))
        self.last_tick = now
        self.update_world(dt,max(1,self.canvas.winfo_width()))
        self.draw_game()
        if time.time()-self.last_save >= 12:
            self.save_game()
        self.root.after(33,lambda:self.tick(session))


if __name__ == "__main__":
    root = tk.Tk()
    game = TaehyunRescue(root)
    root.mainloop()
