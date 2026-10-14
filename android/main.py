"""태현이 구하기(?) - Android/Kivy edition.
Build APK on Linux/macOS/WSL with: buildozer -v android debug
Local accounts and progress are stored on this device only.
"""
__version__ = "1.0.0"

import hashlib
import json
import math
import os
import random
import secrets
import time
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

ZONE_LENGTH = 1450
ZONES = [
    {"name":"별빛 들판", "need":1, "sky":(0.57,0.80,0.91), "ground":(0.34,0.58,0.32), "boss":"별빛 슬라임 대장", "boss_hp":155, "damage":8, "exp":110, "gold":100, "mobs":["초록 슬라임","꽃벌","도토리 도적"]},
    {"name":"버섯 숲", "need":3, "sky":(0.62,0.80,0.71), "ground":(0.31,0.50,0.30), "boss":"버섯 대장", "boss_hp":260, "damage":11, "exp":135, "gold":170, "mobs":["주황 버섯","버섯 병사","덩굴 벌레"]},
    {"name":"바람 절벽", "need":5, "sky":(0.70,0.86,0.91), "ground":(0.42,0.58,0.45), "boss":"회오리 수호자", "boss_hp":370, "damage":14, "exp":165, "gold":240, "mobs":["바람 까마귀","절벽 도마뱀","바람 정령"]},
    {"name":"유령 폐광", "need":7, "sky":(0.53,0.60,0.71), "ground":(0.35,0.34,0.40), "boss":"폐광의 망령", "boss_hp":500, "damage":17, "exp":210, "gold":320, "mobs":["광산 박쥐","작은 유령","철광 골렘"]},
    {"name":"고대 유적", "need":9, "sky":(0.77,0.73,0.60), "ground":(0.53,0.44,0.31), "boss":"봉인된 석상왕", "boss_hp":670, "damage":20, "exp":270, "gold":410, "mobs":["유적 수호병","모래 벌레","고대 석상"]},
    {"name":"불타는 협곡", "need":12, "sky":(0.86,0.67,0.54), "ground":(0.45,0.31,0.27), "boss":"화염 골렘", "boss_hp":850, "damage":24, "exp":340, "gold":500, "mobs":["화염 도마뱀","바위 투사","불꽃 정령"]},
    {"name":"물결 해안", "need":15, "sky":(0.54,0.80,0.84), "ground":(0.25,0.53,0.46), "boss":"폭풍 해신", "boss_hp":1060, "damage":27, "exp":410, "gold":600, "mobs":["조개 전사","파도 게","바다 정령"]},
    {"name":"얼음 성채", "need":18, "sky":(0.61,0.75,0.87), "ground":(0.55,0.70,0.78), "boss":"빙결 기사", "boss_hp":1300, "damage":30, "exp":500, "gold":720, "mobs":["눈보라 늑대","얼음 정령","서리 골렘"]},
    {"name":"구름 신전", "need":21, "sky":(0.78,0.86,0.94), "ground":(0.62,0.72,0.82), "boss":"천공의 문지기", "boss_hp":1600, "damage":33, "exp":580, "gold":850, "mobs":["구름 까마귀","번개 수도사","천둥 정령"]},
    {"name":"저주받은 늪", "need":24, "sky":(0.60,0.67,0.57), "ground":(0.34,0.40,0.29), "boss":"늪의 저주술사", "boss_hp":1950, "damage":36, "exp":700, "gold":1000, "mobs":["늪 독개구리","독안개 유령","가시 덩굴괴물"]},
    {"name":"수정 동굴", "need":27, "sky":(0.63,0.70,0.85), "ground":(0.32,0.39,0.57), "boss":"수정 심장", "boss_hp":2300, "damage":40, "exp":850, "gold":1200, "mobs":["수정 박쥐","보랏빛 골렘","결정 정령"]},
    {"name":"그림자 성", "need":30, "sky":(0.38,0.43,0.54), "ground":(0.22,0.24,0.31), "boss":"그림자 왕", "boss_hp":2800, "damage":43, "exp":1050, "gold":1450, "mobs":["그림자 망령","검은 기사","저주받은 까마귀"]},
    {"name":"어둠의 감옥", "need":34, "sky":(0.22,0.23,0.31), "ground":(0.16,0.15,0.20), "boss":"감금의 마왕", "boss_hp":3600, "damage":47, "exp":1500, "gold":2200, "mobs":["감옥 경비병","어둠의 불꽃","저주 골렘"]},
]
POST_BOSS_NPCS = ["길 잃은 모험가", "숲의 정찰병", "절벽 안내인", "폐광 광부", "유적 연구원", "협곡 상인", "해안 탐험가", "얼음 사제", "구름 신전의 수련생", "늪지 약초꾼", "수정 동굴의 연구원", "성에서 탈출한 기사"]


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
    return salt, digest


def default_save():
    return {"level":1, "exp":0, "gold":0, "attack":10, "max_hp":100, "hp":100,
            "kills":0, "potions":3, "crystals":0, "weapon":0, "armor":0,
            "rebirths":0, "zone":0, "cleared":[False]*len(ZONES), "game_clear":False,
            "pets":[], "skill_points":0, "power_skill":0, "daily_claim":""}


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "login"
        outer = BoxLayout(orientation="vertical", padding=[dp(24), dp(16)], spacing=dp(10))
        outer.add_widget(Label(text="[b]태현이 구하기(?)[/b]", markup=True, font_size="28sp", size_hint_y=.22, color=(1,.84,.49,1)))
        outer.add_widget(Label(text="13개 지역을 돌파하고 최종 보스 뒤에서 태현이를 만나세요!", font_size="14sp", size_hint_y=.12))
        self.user_input = TextInput(hint_text="아이디", multiline=False, size_hint_y=.12, padding=dp(10))
        self.pass_input = TextInput(hint_text="비밀번호", password=True, multiline=False, size_hint_y=.12, padding=dp(10))
        outer.add_widget(self.user_input)
        outer.add_widget(self.pass_input)
        row = BoxLayout(size_hint_y=.13, spacing=dp(8))
        row.add_widget(Button(text="로그인", on_release=lambda *_: self.submit("login")))
        row.add_widget(Button(text="회원가입", on_release=lambda *_: self.submit("signup")))
        outer.add_widget(row)
        self.status = Label(text="연욱 관리자 계정이 기본 제공됩니다.", size_hint_y=.17, font_size="12sp")
        outer.add_widget(self.status)
        self.add_widget(outer)

    def submit(self, mode):
        app = App.get_running_app()
        name = self.user_input.text.strip()
        password = self.pass_input.text
        users = app.load_json(app.users_path, {})
        if mode == "signup":
            if len(name) < 3 or len(name) > 18:
                self.status.text = "아이디는 3~18자로 입력해 주세요."
                return
            if len(password) < 4:
                self.status.text = "비밀번호는 4자 이상이어야 합니다."
                return
            if name == "연욱" or name in users:
                self.status.text = "이미 사용 중이거나 예약된 아이디입니다."
                return
            salt, digest = hash_password(password)
            users[name] = {"salt":salt, "hash":digest, "role":"player", "nickname":name, "banned":False}
            app.write_json(app.users_path, users)
        else:
            record = users.get(name)
            if not record:
                self.status.text = "아이디 또는 비밀번호가 올바르지 않습니다."
                return
            _, digest = hash_password(password, record["salt"])
            if not secrets.compare_digest(digest, record["hash"]):
                self.status.text = "아이디 또는 비밀번호가 올바르지 않습니다."
                return
            if record.get("banned", False):
                self.status.text = "이 계정은 이용이 제한되었습니다."
                return
        app.open_game(name)


class GameWorld(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.hero_x = float(game.data.get("world_x", 100))
        self.jump_h = 0.0
        self.jump_v = 0.0
        self.on_ground = True
        self.direction = 0
        self.monsters = []
        self.spawn_timer = 0.7
        self.attack_timer = 0.0
        self.auto_attack = False
        self.hit_timer = 0.0
        self.message = ""
        self.message_until = 0.0
        self.touch_skill_cd = 0.0
        self.update_event = Clock.schedule_interval(self.update, 1/30)

    def stop(self):
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    @property
    def zone_index(self):
        return max(0, min(len(ZONES)-1, int(self.hero_x // ZONE_LENGTH)))

    @property
    def zone(self):
        return ZONES[self.zone_index]

    @property
    def total_attack(self):
        return int(self.game.data["attack"] + self.game.data["weapon"]*5 + len(self.game.data["pets"])*2 + self.game.data["power_skill"]*3 + self.game.data["rebirths"]*2)

    @property
    def defense(self):
        return int(self.game.data["armor"]*2 + len(self.game.data["pets"]) + self.game.data["rebirths"])

    def say(self, text, seconds=2.5):
        self.message = text
        self.message_until = time.time()+seconds
        self.game.status.text = text

    def move_start(self, direction):
        self.direction = direction

    def move_stop(self, direction):
        if self.direction == direction:
            self.direction = 0

    def jump(self):
        if self.on_ground:
            self.jump_v, self.on_ground = 430, False

    def spawn_mob(self):
        zi = self.zone_index
        z = ZONES[zi]
        if len(self.monsters) >= 4 or any(m.get("boss") for m in self.monsters):
            return
        left, right = zi*ZONE_LENGTH+100, (zi+1)*ZONE_LENGTH-330
        if self.hero_x < (left+right)/2:
            x = min(right, self.hero_x+random.randint(220,390))
        else:
            x = max(left, self.hero_x-random.randint(220,390))
        scale = max(0, int(self.game.data["level"]-z["need"]))
        hp = max(25, 24 + (zi*36) + scale*4)
        self.monsters.append({"x":x, "name":random.choice(z["mobs"]), "hp":hp, "max_hp":hp,
                              "damage":max(3, 6+zi*3), "speed":random.randint(22,43), "boss":False, "cd":.5})

    def spawn_boss(self, idx):
        if self.game.data["cleared"][idx] or any(m.get("boss") for m in self.monsters):
            return
        z = ZONES[idx]
        self.monsters.clear()
        self.monsters.append({"x":(idx+1)*ZONE_LENGTH-215, "name":z["boss"], "hp":z["boss_hp"],
                              "max_hp":z["boss_hp"], "damage":z["damage"], "speed":18+idx*1.7,
                              "boss":True, "cd":.8, "zone":idx})
        self.say(f"지역 수호자 등장: {z['boss']}! 공격하고 물약을 활용하세요.", 4)

    def attack(self, multiplier=1.0, all_near=False):
        if self.game.overlay_open:
            return
        now = time.time()
        if now-self.attack_timer < .34:
            return
        self.attack_timer = now
        targets = [m for m in self.monsters if abs(m["x"]-self.hero_x) < (245 if m.get("boss") else 150)]
        if not targets:
            self.say("공격 범위 안에 몬스터가 없습니다.", 1.3)
            return
        if not all_near:
            targets = [min(targets, key=lambda m:abs(m["x"]-self.hero_x))]
        for mob in list(targets):
            damage = max(1, int(self.total_attack*multiplier*random.uniform(.9,1.1)))
            mob["hp"] -= damage
            if mob["hp"] <= 0 and mob in self.monsters:
                if mob.get("boss"):
                    self.boss_defeated(int(mob["zone"]))
                else:
                    self.monsters.remove(mob)
                    d = self.game.data
                    d["kills"] += 1
                    d["gold"] += random.randint(6,15)+self.zone_index*3
                    self.gain_exp(8+self.zone_index*3)
                    if random.random() < .12:
                        d["potions"] += 1
                        self.say("몬스터가 회복 물약을 떨어뜨렸습니다!")
                    elif random.random() < .12:
                        d["crystals"] += 1
                        self.say("강화 수정을 획득했습니다!")
        self.game.refresh_hud()

    def boss_defeated(self, idx):
        d = self.game.data
        mob = next((m for m in self.monsters if m.get("boss") and m.get("zone")==idx), None)
        if mob and mob in self.monsters:
            self.monsters.remove(mob)
        d["cleared"][idx] = True
        d["gold"] += ZONES[idx]["gold"]
        d["potions"] += 2
        d["crystals"] += 2+idx
        d["boss_kills"] = int(d.get("boss_kills",0))+1
        if idx == 0 and "꼬마 슬라임" not in d["pets"]:
            d["pets"].append("꼬마 슬라임")
        elif idx == 2 and "불꽃 여우" not in d["pets"]:
            d["pets"].append("불꽃 여우")
        elif idx == 4 and "얼음 정령 친구" not in d["pets"]:
            d["pets"].append("얼음 정령 친구")
        self.gain_exp(ZONES[idx]["exp"])
        d["hp"] = d["max_hp"]
        if idx < len(ZONES)-1:
            bonus = 100+idx*75
            d["gold"] += bonus
            d["potions"] += 1
            d["crystals"] += 1
            self.hero_x = (idx+1)*ZONE_LENGTH+85
            self.game.save_game()
            npc = POST_BOSS_NPCS[idx]
            self.game.show_npc_dialog(npc, "태현이는 여기에 없어요. 일단 이거 받으세요.",
                                      f"보상: 골드 {bonus} · 회복 물약 1개 · 강화 수정 1개", final=False)
        else:
            d["game_clear"] = True
            self.hero_x = (len(ZONES)-1)*ZONE_LENGTH+ZONE_LENGTH-260
            self.game.save_game()
            self.game.show_npc_dialog("태현", f"고마워요 {self.game.nickname}, 환생할 기회를 줄게요.",
                                      "최종 보스 격파! 태현이를 구출했습니다.", final=True)
        self.game.refresh_hud()

    def gain_exp(self, amount):
        d=self.game.data
        d["exp"] += int(amount)
        while d["exp"] >= d["level"]*30:
            d["exp"] -= d["level"]*30
            d["level"] += 1
            d["attack"] += 3
            d["max_hp"] += 12
            d["hp"] = d["max_hp"]
            d["skill_points"] += 1
        self.game.refresh_hud()

    def use_potion(self):
        d=self.game.data
        if d["potions"] <= 0:
            return self.say("물약이 없습니다. 상점에서 구매하세요.")
        if d["hp"] >= d["max_hp"]:
            return self.say("체력이 이미 가득 찼습니다.")
        heal=min(65+d["level"]*2,d["max_hp"]-d["hp"])
        d["hp"] += heal; d["potions"] -= 1
        self.say(f"회복 물약 사용! HP +{heal}")
        self.game.refresh_hud()

    def skill_one(self):
        self.attack(2.0)

    def skill_heal(self):
        d=self.game.data
        if d["level"] < 3:
            return self.say("회복 기운은 레벨 3부터 사용할 수 있습니다.")
        healed=min(int(d["max_hp"]*.35), d["max_hp"]-d["hp"])
        d["hp"] += healed
        self.say(f"회복 기운! HP +{healed}")
        self.game.refresh_hud()

    def update(self, dt):
        if not self.parent or self.game.overlay_open:
            self.redraw()
            return
        dt=min(dt,.05)
        d=self.game.data
        zi=self.zone_index
        z=ZONES[zi]
        old_x=self.hero_x
        self.hero_x += self.direction*255*dt
        self.hero_x=max(35,min(ZONE_LENGTH*len(ZONES)-35,self.hero_x))
        # The camera is computed from hero_x each frame below, so it keeps tracking smoothly.
        next_gate=(zi+1)*ZONE_LENGTH
        if not d["cleared"][zi] and self.hero_x >= next_gate-320:
            self.hero_x=next_gate-320
            if not any(m.get("boss") for m in self.monsters):
                self.spawn_boss(zi)
        elif d["cleared"][zi] and zi < len(ZONES)-1 and self.hero_x >= next_gate-30:
            if d["level"] < ZONES[zi+1]["need"]:
                self.hero_x=next_gate-31
                self.say(f"다음 지역은 레벨 {ZONES[zi+1]['need']}부터 입장할 수 있습니다.")
        if not self.on_ground:
            self.jump_h += self.jump_v*dt
            self.jump_v -= 1050*dt
            if self.jump_h <= 0:
                self.jump_h=0; self.jump_v=0; self.on_ground=True
        self.spawn_timer += dt
        if self.spawn_timer > 2.0:
            self.spawn_timer=0
            self.spawn_mob()
        for mob in list(self.monsters):
            dx=self.hero_x-mob["x"]
            touch=70 if mob.get("boss") else 35
            if abs(dx)>touch:
                mob["x"] += math.copysign(mob["speed"]*dt,dx)
            mob["cd"] = max(0,mob["cd"]-dt)
            if abs(dx)<(83 if mob.get("boss") else 45) and self.jump_h<12 and mob["cd"]<=0:
                damage=max(1,int(mob["damage"])-self.defense)
                d["hp"] -= damage; mob["cd"] = 1.0 if mob.get("boss") else 1.2
                if d["hp"] <= 0:
                    d["hp"] = max(1,int(d["max_hp"]*.6))
                    self.hero_x=max(100,int(d.get("checkpoint",0))*ZONE_LENGTH+100)
                    self.jump_h=self.jump_v=0; self.on_ground=True
                    self.monsters=[m for m in self.monsters if m.get("boss")]
                    self.say("쓰러졌다가 체크포인트에서 다시 일어났습니다.")
                    break
        if self.auto_attack and self.monsters and time.time()-self.attack_timer>.45:
            if any(abs(m["x"]-self.hero_x)<(245 if m.get("boss") else 150) for m in self.monsters):
                self.attack()
        self.game.data["world_x"] = self.hero_x
        if time.time()-self.game.last_save > 8:
            self.game.save_game()
        self.redraw()

    def redraw(self, *_):
        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return
        d=self.game.data; zi=self.zone_index; z=ZONES[zi]
        w,h=self.width,self.height
        camera=max(0,min(self.hero_x-w*.42,ZONE_LENGTH*len(ZONES)-w))
        gy=self.y+dp(42)
        sx=self.x
        with self.canvas:
            Color(*z["sky"]); Rectangle(pos=(sx,self.y),size=(w,h))
            # rolling hills, with parallax tied to camera
            Color(z["ground"][0]*.9,z["ground"][1]*1.12,z["ground"][2]*1.05,1)
            for i in range(-1,int(w/dp(190))+3):
                hx=sx+i*dp(190)-(camera*.2 % dp(190))
                Ellipse(pos=(hx,gy+dp(22)),size=(dp(240),dp(110)))
            Color(*z["ground"]); Rectangle(pos=(sx, self.y),size=(w,gy-self.y))
            Color(.7,.82,.56,1); Rectangle(pos=(sx,gy),size=(w,dp(7)))
            # region decorations
            for i in range(-1,int(w/dp(150))+3):
                dx=sx+i*dp(150)-(camera % dp(150))
                if zi in (1,):
                    Color(.78,.44,.35,1); Ellipse(pos=(dx,gy+dp(12)),size=(dp(26),dp(25)))
                    Color(.91,.83,.68,1); Rectangle(pos=(dx+dp(9),gy-dp(5)),size=(dp(8),dp(22)))
                elif zi in (5,):
                    Color(.59,.34,.27,1); Line(points=[dx,gy,dx+dp(25),gy+dp(53),dx+dp(54),gy],width=2)
                    Color(.95,.42,.22,1); Line(points=[dx+dp(12),gy+dp(5),dx+dp(24),gy+dp(24),dx+dp(32),gy+dp(9)],width=2)
                elif zi in (7,):
                    Color(.75,.86,.93,1); Line(points=[dx+dp(3),gy+dp(5),dx+dp(18),gy+dp(52),dx+dp(36),gy+dp(11)],width=2)
                elif zi in (11,12):
                    Color(.24,.25,.34,1); Rectangle(pos=(dx+dp(14),gy+dp(4)),size=(dp(36),dp(72)))
                    Color(.64,.49,.66,1); Line(points=[dx+dp(10),gy+dp(75),dx+dp(32),gy+dp(96),dx+dp(54),gy+dp(75)],width=2)
                else:
                    Color(.22,.48,.32,1); Rectangle(pos=(dx+dp(20),gy+dp(5)),size=(dp(9),dp(42)))
                    Color(.23,.48,.31,1); Ellipse(pos=(dx,gy+dp(28)),size=(dp(50),dp(48)))
            # gate and the boss gate barrier
            gate=(zi+1)*ZONE_LENGTH-camera
            if -dp(40)<gate<w+dp(40):
                Color(.3,.24,.32,1); Rectangle(pos=(sx+gate-dp(20),gy),size=(dp(40),dp(86)))
                Color(.4,.85,.57,1) if d["cleared"][zi] else Color(.88,.32,.42,1)
                Line(rectangle=(sx+gate-dp(21),gy,dp(42),dp(88)),width=2)
            # mobs
            for mob in self.monsters:
                mx=sx+mob["x"]-camera
                if mx < sx-dp(70) or mx > sx+w+dp(70):
                    continue
                size=dp(60 if mob.get("boss") else 34)
                Color(.72,.31,.37,1) if mob.get("boss") else Color(.44,.72,.47,1)
                Ellipse(pos=(mx-size/2,gy+dp(2)),size=(size,size*.8))
                Color(1,.95,.82,1)
                Ellipse(pos=(mx-size*.22,gy+size*.36),size=(dp(5),dp(5)))
                Ellipse(pos=(mx+size*.08,gy+size*.36),size=(dp(5),dp(5)))
                # health bar
                Color(.16,.17,.21,1); Rectangle(pos=(mx-size/2,gy+size+dp(6)),size=(size,dp(5)))
                Color(.86,.29,.34,1); Rectangle(pos=(mx-size/2,gy+size+dp(6)),size=(size*max(0,mob["hp"])/max(1,mob["max_hp"]),dp(5)))
            # player
            px=sx+self.hero_x-camera
            py=gy+dp(6)+self.jump_h*dp(.65)
            Color(.17,.20,.27,1); Ellipse(pos=(px-dp(16),gy-dp(5)),size=(dp(32),dp(8)))
            Color(.27,.49,.76,1); RoundedRectangle(pos=(px-dp(12),py+dp(3)),size=(dp(24),dp(27)),radius=[dp(4), dp(4), dp(4), dp(4)])
            Color(.94,.75,.59,1); Ellipse(pos=(px-dp(15),py+dp(24)),size=(dp(30),dp(30)))
            Color(.29,.20,.19,1); Ellipse(pos=(px-dp(16),py+dp(43)),size=(dp(32),dp(12)))
            # character's name label as a tiny line above sprite
            Color(1,.90,.63,1); Line(points=[px-dp(22),py+dp(60),px+dp(22),py+dp(60)],width=1.4)
        # overlay labels are normal Kivy widgets via HUD, keep scene smooth.


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.data = default_save()
        self.username = ""
        self.nickname = ""
        self.role = "player"
        self.overlay_open = False
        self.last_save = time.time()
        root=BoxLayout(orientation="vertical",padding=dp(5),spacing=dp(4))
        header=BoxLayout(size_hint_y=None,height=dp(32),spacing=dp(8))
        self.title_label=Label(text="태현이 구하기(?)",font_size="17sp",color=(1,.84,.49,1),size_hint_x=.45)
        self.stage_label=Label(text="STAGE 1/13",font_size="13sp",size_hint_x=.55)
        header.add_widget(self.title_label);header.add_widget(self.stage_label);root.add_widget(header)
        self.hud=Label(text="HP 100/100 · Lv.1 · 골드 0",size_hint_y=None,height=dp(28),font_size="12sp")
        root.add_widget(self.hud)
        self.world=GameWorld(self,size_hint_y=.63)
        root.add_widget(self.world)
        self.status=Label(text="이동해서 지역 보스를 찾아보세요.",size_hint_y=None,height=dp(24),font_size="11sp")
        root.add_widget(self.status)
        move_row=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(4))
        left=Button(text="◀",font_size="20sp"); right=Button(text="▶",font_size="20sp")
        left.bind(on_press=lambda *_:self.world.move_start(-1),on_release=lambda *_:self.world.move_stop(-1))
        right.bind(on_press=lambda *_:self.world.move_start(1),on_release=lambda *_:self.world.move_stop(1))
        move_row.add_widget(left);move_row.add_widget(right)
        for label,fn in [("점프",self.world.jump),("공격",self.world.attack),("자동",self.toggle_auto),("스킬 1",self.world.skill_one),("회복",self.world.skill_heal),("물약",self.world.use_potion)]:
            move_row.add_widget(Button(text=label,on_release=lambda _b,callback=fn:callback(),font_size="11sp"))
        root.add_widget(move_row)
        menu_row=BoxLayout(size_hint_y=None,height=dp(38),spacing=dp(4))
        for label,fn in [("성장",self.open_upgrade),("상점",self.open_shop),("지도",self.open_map),("임무",self.open_quests),("저장",self.save_game)]:
            menu_row.add_widget(Button(text=label,on_release=lambda _b,callback=fn:callback(),font_size="11sp"))
        self.admin_btn = Button(text="관리자",on_release=lambda *_:self.open_admin(),font_size="10sp")
        menu_row.add_widget(self.admin_btn)
        menu_row.add_widget(Button(text="로그아웃",on_release=lambda *_:self.app.logout(),font_size="10sp"))
        root.add_widget(menu_row)
        self.add_widget(root)
        self.hud_clock = Clock.schedule_interval(lambda _dt:self.refresh_hud(),.35)

    def load_data(self, username, role, nickname):
        self.username,self.role,self.nickname=username,role,nickname
        self.admin_btn.disabled = (role != "admin")
        self.admin_btn.opacity = 1 if role == "admin" else 0.45
        data=self.app.load_json(self.app.saves_path,{})
        saved=data.get(username,{})
        fresh=default_save();fresh.update(saved)
        if len(fresh.get("cleared",[])) != len(ZONES):
            old=list(fresh.get("cleared",[]))
            fresh["cleared"]=(old+[False]*len(ZONES))[:len(ZONES)]
        self.data=fresh
        today=time.strftime("%Y-%m-%d")
        if self.data.get("daily_claim","") != today:
            self.data["gold"] += 100+self.data["level"]*10
            self.data["potions"] += 2
            self.data["daily_claim"] = today
            self.status.text="접속 보상! 골드와 물약을 받았습니다."
        self.world.hero_x=float(self.data.get("world_x", max(80, int(self.data.get("zone",0))*ZONE_LENGTH+120)))
        if self.data.get("game_clear"):
            self.show_npc_dialog("태현",f"고마워요 {self.nickname}, 환생할 기회를 줄게요.","태현이 구출 완료!",final=True)
        self.refresh_hud()

    def refresh_hud(self, *_):
        if not hasattr(self,"data") or not self.data:
            return
        d=self.data
        zi=self.world.zone_index if hasattr(self,"world") else int(d.get("zone",0))
        self.stage_label.text=f"STAGE {zi+1}/13 · {ZONES[zi]['name']}"
        self.title_label.text=f"태현이 구하기(?)  · 환생 {d.get('rebirths',0)}회"
        attack=self.world.total_attack if hasattr(self,"world") else d["attack"]
        self.hud.text=f"{self.nickname}  Lv.{d['level']}  · HP {d['hp']}/{d['max_hp']}  · 공격 {attack}  · 골드 {d['gold']:,}  · 물약 {d['potions']}"

    def toggle_auto(self):
        self.world.auto_attack=not self.world.auto_attack
        self.world.say("자동 공격 켜짐" if self.world.auto_attack else "자동 공격 꺼짐")

    def save_game(self, *_):
        if not self.username:
            return
        self.data["world_x"]=self.world.hero_x
        self.data["zone"]=self.world.zone_index
        self.app.save_user_data(self.username,self.data)
        self.last_save=time.time()
        self.world.say("저장 완료!",1.2)

    def on_pre_leave(self,*_):
        self.save_game()
        if hasattr(self, "hud_clock") and self.hud_clock:
            self.hud_clock.cancel()
            self.hud_clock = None
        if hasattr(self, "world"):
            self.world.stop()

    def popup(self,title,body,buttons):
        layout=BoxLayout(orientation="vertical",padding=dp(12),spacing=dp(8))
        layout.add_widget(Label(text=body,markup=True,halign="center",valign="middle"))
        row=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(8))
        for label,fn in buttons:
            row.add_widget(Button(text=label,on_release=lambda _b,callback=fn: (popup.dismiss(),callback()),font_size="12sp"))
        layout.add_widget(row)
        popup=Popup(title=title,content=layout,size_hint=(.9,.62),auto_dismiss=False)
        self.overlay_open=True
        popup.bind(on_dismiss=lambda *_:setattr(self,"overlay_open",False))
        popup.open()
        return popup

    def show_npc_dialog(self,name,line,reward,final=False):
        layout=BoxLayout(orientation="vertical",padding=dp(16),spacing=dp(10))
        tag=Label(text=f"[b]◆ {name} ◆[/b]",markup=True,font_size="22sp",color=(1,.84,.49,1),size_hint_y=.22)
        layout.add_widget(tag)
        layout.add_widget(Label(text=line,font_size="18sp",halign="center",valign="middle"))
        layout.add_widget(Label(text=reward,font_size="12sp",color=(.67,.91,.73,1),halign="center"))
        row=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(8))
        popup=Popup(title="최종 장면" if final else "보스 격파 후",content=layout,size_hint=(.91,.63),auto_dismiss=False)
        self.overlay_open=True
        popup.bind(on_dismiss=lambda *_:setattr(self,"overlay_open",False))
        if final:
            row.add_widget(Button(text="환생할 기회 받기",on_release=lambda *_:(popup.dismiss(),self.rebirth())))
            row.add_widget(Button(text="나중에",on_release=lambda *_:popup.dismiss()))
        else:
            row.add_widget(Button(text="보상 받고 계속",on_release=lambda *_:popup.dismiss()))
        layout.add_widget(row)
        popup.open()

    def rebirth(self):
        d=self.data
        d["rebirths"] += 1
        d["level"]=1;d["exp"]=0;d["gold"]=100
        d["attack"]=10+d["rebirths"]*5
        d["max_hp"]=100+d["rebirths"]*25;d["hp"]=d["max_hp"]
        d["kills"]=0;d["potions"]=5;d["crystals"]=0;d["weapon"]=0;d["armor"]=0
        d["zone"]=0;d["world_x"]=100;d["cleared"]=[False]*len(ZONES);d["game_clear"]=False
        d["skill_points"]=0;d["power_skill"]=0
        self.world.hero_x=100;self.world.monsters=[];self.world.jump_h=0;self.world.jump_v=0;self.world.on_ground=True
        self.save_game();self.refresh_hud();self.world.say(f"환생 {d['rebirths']}회! 영구 보너스를 얻었습니다.",5)

    def open_upgrade(self):
        d=self.data
        self.popup("성장과 강화",f"골드: {d['gold']:,}\n공격력: {self.world.total_attack}\n최대 HP: {d['max_hp']}\n무기 +{d['weapon']} · 방어구 +{d['armor']}\n스킬 포인트: {d['skill_points']}",[
            (f"공격 +5 ({d['level']*30}G)",lambda:self.buy_upgrade("attack",d['level']*30)),
            (f"HP +25 ({d['level']*25}G)",lambda:self.buy_upgrade("hp",d['level']*25)),
            (f"무기 강화 ({80+d['weapon']*95}G)",lambda:self.buy_upgrade("weapon",80+d['weapon']*95)),
            ("닫기",lambda:None)])

    def buy_upgrade(self,kind,cost):
        d=self.data
        if d["gold"]<cost:
            self.world.say("골드가 부족합니다.");return
        d["gold"]-=cost
        if kind=="attack":d["attack"]+=5
        elif kind=="hp":d["max_hp"]+=25;d["hp"]=d["max_hp"]
        elif kind=="weapon":
            if d["crystals"]>0:d["crystals"]-=1;d["weapon"]+=2
            else:d["weapon"]+=1
        self.refresh_hud();self.save_game()

    def open_shop(self):
        d=self.data
        self.popup("여행 상점",f"보유 골드: {d['gold']:,}\n물약 {d['potions']}개 · 강화 수정 {d['crystals']}개",[
            ("물약 구매 (25G)",lambda:self.buy_item("potion",25)),
            ("수정 구매 (115G)",lambda:self.buy_item("crystal",115)),
            ("공격 주문서 (175G)",lambda:self.buy_item("scroll",175)),
            ("닫기",lambda:None)])

    def buy_item(self,kind,cost):
        d=self.data
        if d["gold"]<cost:return self.world.say("골드가 부족합니다.")
        d["gold"]-=cost
        if kind=="potion":d["potions"]+=1
        elif kind=="crystal":d["crystals"]+=1
        else:d["attack"]+=10
        self.refresh_hud();self.save_game();self.world.say("구매했습니다!")

    def open_map(self):
        wrap=BoxLayout(orientation="vertical",spacing=dp(5),padding=dp(8))
        scroll=GridLayout(cols=1,spacing=dp(3),size_hint_y=None)
        scroll.bind(minimum_height=scroll.setter("height"))
        for i,z in enumerate(ZONES):
            enabled=(i==0 or (all(self.data["cleared"][j] for j in range(i)) and self.data["level"]>=z["need"]))
            status="클리어" if self.data["cleared"][i] else ("입장 가능" if enabled else f"Lv.{z['need']} 및 이전 보스 클리어 필요")
            btn=Button(text=f"{i+1}. {z['name']} — {status}",size_hint_y=None,height=dp(36),disabled=not enabled)
            btn.bind(on_release=lambda _b,idx=i:self.teleport_zone(idx,popup))
            scroll.add_widget(btn)
        from kivy.uix.scrollview import ScrollView
        sv=ScrollView();sv.add_widget(scroll);wrap.add_widget(sv)
        close=Button(text="닫기",size_hint_y=None,height=dp(42));wrap.add_widget(close)
        popup=Popup(title="13개 지역 지도",content=wrap,size_hint=(.88,.85))
        close.bind(on_release=popup.dismiss);self.overlay_open=True;popup.bind(on_dismiss=lambda *_:setattr(self,"overlay_open",False));popup.open()

    def teleport_zone(self,idx,popup):
        popup.dismiss()
        if idx and not all(self.data["cleared"][j] for j in range(idx)):
            return self.world.say("앞 지역의 보스를 먼저 쓰러뜨리세요.")
        self.world.hero_x=idx*ZONE_LENGTH+120
        self.world.monsters=[];self.data["zone"]=idx;self.save_game();self.refresh_hud()
        self.world.say(f"{ZONES[idx]['name']}으로 이동했습니다.")

    def open_quests(self):
        d=self.data
        self.popup("모험 기록",f"지역 클리어: {sum(d['cleared'])}/13\n몬스터 처치: {d['kills']}\n보스 처치: {d.get('boss_kills',0)}\n환생 횟수: {d['rebirths']}\n\n목표: 각 지역 보스를 차례로 처치하세요. 1~12번째 보스 뒤에는 다른 인물이 보상을 주고, 13번째 보스 뒤에 태현이를 만납니다.",[("확인",lambda:None)])

    def open_admin(self):
        if self.role!="admin":return
        d=self.data
        self.popup("관리자 도구", "현재 기기의 계정 데이터에만 적용됩니다.",[
            ("골드 +10,000",lambda:self.admin_action("gold")),
            ("레벨 +10",lambda:self.admin_action("level")),
            ("지역 전부 해금",lambda:self.admin_action("unlock")),
            ("현재 진행 초기화",lambda:self.admin_action("reset")),
        ])

    def admin_action(self,action):
        d=self.data
        if action=="gold":d["gold"]+=10000
        elif action=="level":d["level"]+=10;d["attack"]+=30;d["max_hp"]+=120;d["hp"]=d["max_hp"]
        elif action=="unlock":d["cleared"]=[True]*len(ZONES);d["cleared"][-1]=False;self.world.hero_x=12*ZONE_LENGTH+80;self.world.monsters=[]
        elif action=="reset":
            fresh=default_save();fresh["rebirths"]=d.get("rebirths",0);self.data=fresh;self.world.hero_x=100;self.world.monsters=[]
        self.refresh_hud();self.save_game();self.world.say("관리자 작업이 적용됐습니다.")

    def on_touch_down(self,touch):
        return super().on_touch_down(touch)


class TaehyunRescueApp(App):
    def build(self):
        self.title="태현이 구하기(?)"
        self.users_path=Path(self.user_data_dir)/"users.json"
        self.saves_path=Path(self.user_data_dir)/"saves.json"
        self.seed_admin()
        self.manager=ScreenManager(transition=FadeTransition(duration=.12))
        self.login=LoginScreen(name="login")
        self.manager.add_widget(self.login)
        self.current_game=None
        Window.clearcolor=(.08,.10,.15,1)
        return self.manager

    def load_json(self,path,default):
        try:return json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError,TypeError):return default

    def write_json(self,path,data):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix(path.suffix+".tmp")
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(path)

    def seed_admin(self):
        users=self.load_json(self.users_path,{})
        if "연욱" not in users:
            salt,digest=hash_password("151013",None)
            users["연욱"]={"salt":salt,"hash":digest,"role":"admin","nickname":"연욱","banned":False}
        else:
            users["연욱"]["role"]="admin"
            users["연욱"]["nickname"]="연욱"
        self.write_json(self.users_path,users)

    def open_game(self,username):
        users=self.load_json(self.users_path,{})
        record=users[username]
        if self.current_game:
            self.manager.remove_widget(self.current_game)
        self.current_game=GameScreen(name="game")
        self.manager.add_widget(self.current_game)
        self.current_game.load_data(username,record.get("role","player"),record.get("nickname",username))
        self.manager.current="game"

    def save_user_data(self,username,data):
        saves=self.load_json(self.saves_path,{})
        saves[username]=data
        self.write_json(self.saves_path,saves)

    def save_game(self):
        if self.current_game and self.current_game.username:
            self.current_game.save_game()

    def logout(self):
        self.save_game()
        self.manager.current="login"
        if self.current_game:
            self.manager.remove_widget(self.current_game)
            self.current_game=None

    def on_pause(self):
        self.save_game()
        return True

    def on_stop(self):
        self.save_game()


if __name__ == "__main__":
    TaehyunRescueApp().run()
