"""Shared Pygame game engine for desktop and Android."""
from __future__ import annotations

import copy
import json
import math
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from queue import SimpleQueue

import pygame

API_BASE = os.getenv("TAEHYUN_API_URL", "https://taehyun-rescue-api.onrender.com").rstrip("/")
W, H, FPS = 960, 540, 60
ZONE_LENGTH = 1450

ZONES = [
 {"name":"별빛 들판","need":1,"sky":(145,204,232),"hill":(118,183,158),"ground":(87,148,81),"story":"수상한 발자국이 별빛 들판에 남아 있다.","mobs":["초록 슬라임","꽃벌","도토리 도적"],"boss":"별빛 슬라임 대장","hp":155,"damage":8,"exp":110,"gold":100},
 {"name":"버섯 숲","need":3,"sky":(159,205,181),"hill":(103,154,112),"ground":(80,128,77),"story":"버섯 병사들이 숲속 길을 막고 있다.","mobs":["주황 버섯","버섯 병사","덩굴 벌레"],"boss":"버섯 대장","hp":260,"damage":11,"exp":135,"gold":170},
 {"name":"바람 절벽","need":5,"sky":(180,219,231),"hill":(119,167,183),"ground":(107,147,107),"story":"강한 바람을 뚫고 절벽 정상에 올라야 한다.","mobs":["바람 까마귀","절벽 도마뱀","바람 정령"],"boss":"회오리 수호자","hp":370,"damage":14,"exp":165,"gold":240},
 {"name":"유령 폐광","need":7,"sky":(136,153,181),"hill":(102,116,142),"ground":(98,93,105),"story":"폐광에서 태현이의 흔적이 적힌 쪽지를 찾았다.","mobs":["광산 박쥐","작은 유령","철광 골렘"],"boss":"폐광의 망령","hp":500,"damage":17,"exp":210,"gold":320},
 {"name":"고대 유적","need":9,"sky":(196,185,154),"hill":(140,148,117),"ground":(135,112,78),"story":"오래된 석판에는 열세 개의 관문이 그려져 있다.","mobs":["유적 수호병","모래 벌레","고대 석상"],"boss":"봉인된 석상왕","hp":670,"damage":20,"exp":270,"gold":410},
 {"name":"불타는 협곡","need":12,"sky":(219,172,138),"hill":(163,108,95),"ground":(115,80,71),"story":"불길 너머에 바닷길로 이어지는 다리가 있다.","mobs":["화염 도마뱀","바위 투사","불꽃 정령"],"boss":"화염 골렘","hp":850,"damage":24,"exp":340,"gold":500},
 {"name":"물결 해안","need":15,"sky":(139,203,215),"hill":(92,170,158),"ground":(64,139,120),"story":"파도 소리 너머에서 도움을 요청하는 소리가 들린다.","mobs":["조개 전사","파도 게","바다 정령"],"boss":"폭풍 해신","hp":1060,"damage":27,"exp":410,"gold":600},
 {"name":"얼음 성채","need":18,"sky":(155,191,223),"hill":(117,149,184),"ground":(145,182,204),"story":"얼어붙은 성채를 넘으면 구름 위로 갈 수 있다.","mobs":["눈보라 늑대","얼음 정령","서리 골렘"],"boss":"빙결 기사","hp":1300,"damage":30,"exp":500,"gold":720},
 {"name":"구름 신전","need":21,"sky":(199,220,240),"hill":(142,172,211),"ground":(182,200,217),"story":"신전의 문지기가 마왕이 지나간 방향을 알려준다.","mobs":["구름 까마귀","번개 수도사","천둥 정령"],"boss":"천공의 문지기","hp":1600,"damage":33,"exp":580,"gold":850},
 {"name":"저주받은 늪","need":24,"sky":(154,170,145),"hill":(100,125,102),"ground":(89,106,78),"story":"독안개 속에서 감옥으로 통하는 표식을 발견했다.","mobs":["늪 독개구리","독안개 유령","가시 덩굴괴물"],"boss":"늪의 저주술사","hp":1950,"damage":36,"exp":700,"gold":1000},
 {"name":"수정 동굴","need":27,"sky":(162,180,216),"hill":(110,127,181),"ground":(82,100,137),"story":"빛나는 수정 속에 마지막 성의 위치가 비친다.","mobs":["수정 박쥐","보랏빛 골렘","결정 정령"],"boss":"수정 심장","hp":2300,"damage":40,"exp":850,"gold":1200},
 {"name":"그림자 성","need":30,"sky":(98,110,138),"hill":(66,69,95),"ground":(57,61,80),"story":"마지막 문 안쪽에 태현이를 가둔 마왕이 있다.","mobs":["그림자 망령","검은 기사","저주받은 까마귀"],"boss":"그림자 왕","hp":2800,"damage":43,"exp":1050,"gold":1450},
 {"name":"어둠의 감옥","need":34,"sky":(56,59,80),"hill":(41,43,61),"ground":(41,38,50),"story":"마지막 문 뒤에 태현이가 갇혀 있다. 마왕을 물리치자!","mobs":["감옥 경비병","어둠의 불꽃","저주 골렘"],"boss":"감금의 마왕","hp":3600,"damage":47,"exp":1500,"gold":2200},
]
NPCS = ["길 잃은 모험가","숲의 정찰병","절벽 안내인","폐광 광부","유적 연구원","협곡 상인","해안 탐험가","얼음 사제","구름 신전의 수련생","늪지 약초꾼","수정 동굴의 연구원","성에서 탈출한 기사"]
WORLD_W = ZONE_LENGTH * len(ZONES)


def default_save():
    return {
        "player_x":160.0,"level":1,"exp":0,"gold":0,"attack":10,"max_hp":100,"hp":100,
        "kills":0,"weapon_level":0,"armor_level":0,"potions":3,"crystals":0,"boss_kills":0,
        "cleared_zones":[False]*len(ZONES),"checkpoint_zone":0,"skill_points":0,
        "skill_levels":{"power":0,"vitality":0},"claimed_quests":[],"achievements":[],"pets":[],
        "daily_claim":"","game_clear":False,"rebirth_count":0,"current_dialogue":None
    }


def api_request(path, method="GET", payload=None, token=None, timeout=10):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept":"application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(API_BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("detail","서버 요청에 실패했어.")
        except Exception:
            detail = "서버 요청에 실패했어."
        raise RuntimeError(str(detail)) from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("온라인 서버에 연결할 수 없어. 잠시 후 다시 시도해 줘.") from exc


def clamp(value, low, high):
    return max(low, min(high, value))


def mix(a, b, ratio):
    ratio = clamp(ratio, 0.0, 1.0)
    return tuple(round(x+(y-x)*ratio) for x,y in zip(a,b))


class ChunsangGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("천상 키우기")
        self.android = sys.platform == "android" or "ANDROID_ARGUMENT" in os.environ
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) if self.android else pygame.display.set_mode((W,H), pygame.RESIZABLE)
        self.canvas = pygame.Surface((W,H))
        self.clock = pygame.time.Clock()
        self.running = True
        self.view = "login"
        self.auth_mode = "login"
        self.active_field = "username"
        self.username_input = ""
        self.password_input = ""
        self.notice_text = "기존 온라인 계정으로 로그인하거나 새 계정을 만들어 줘."
        self.notice_error = False
        self.token = ""
        self.current_user = ""
        self.nickname = ""
        self.role = "player"
        self.data = default_save()
        self.queue = SimpleQueue()
        self.tasks = set()
        self.save_lock = threading.Lock()
        self.save_again = False
        self.save_status = "온라인 서버 연결"
        self.last_save = time.monotonic()
        self.buttons = []
        self.fields = {}
        self.keys = set()
        self.pointer_held = set()
        self.enemies = []
        self.effects = []
        self.player_y = 0.0
        self.jump_v = 0.0
        self.on_ground = True
        self.facing = 1
        self.invulnerable = 0.0
        self.attack_cd = 0.0
        self.attack_flash = 0.0
        self.spawn_timer = 0.0
        self.camera_x = 0.0
        self.toast = ""
        self.toast_until = 0.0
        self.toast_error = False
        self.admin_users = []
        self.admin_loading = False
        self.admin_offset = 0
        self.fonts = {}
        self.load_fonts()
        try:
            pygame.key.start_text_input()
        except Exception:
            pass

    def load_fonts(self):
        paths = []
        if self.android:
            paths.extend(["/system/fonts/NotoSansCJK-Regular.ttc","/system/fonts/NotoSansKR-Regular.otf"])
        if sys.platform == "win32":
            paths.extend([r"C:\Windows\Fonts\malgun.ttf",r"C:\Windows\Fonts\segoeui.ttf"])
        paths.extend(["/usr/share/fonts/truetype/nanum/NanumGothic.ttf","/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc","/System/Library/Fonts/AppleSDGothicNeo.ttc"])
        path = next((p for p in paths if os.path.exists(p)), None)
        for size in (9,10,11,12,13,14,16,18,21,24,28,32):
            try:
                self.fonts[size] = pygame.font.Font(path,size) if path else pygame.font.SysFont("malgungothic,noto sans cjk kr,arial",size)
            except Exception:
                self.fonts[size] = pygame.font.Font(None,size)

    def font(self, size):
        return self.fonts.get(size,self.fonts[14])

    def text(self, value, x, y, size=14, color=(237,240,233), center=False):
        surface = self.font(size).render(str(value),True,color)
        rect = surface.get_rect()
        if center: rect.center=(int(x),int(y))
        else: rect.topleft=(int(x),int(y))
        self.canvas.blit(surface,rect)
        return rect

    def panel(self, rect, fill=(31,40,53), edge=(53,66,82), radius=12):
        pygame.draw.rect(self.canvas,fill,rect,border_radius=radius)
        pygame.draw.rect(self.canvas,edge,rect,1,border_radius=radius)

    def button(self, rect, label, action, style="normal", small=False):
        rect=pygame.Rect(rect)
        palette={
            "normal":((43,54,69),(76,91,109),(238,241,237)),
            "primary":((190,151,86),(222,190,127),(28,31,36)),
            "quiet":((29,37,48),(57,69,84),(205,214,222)),
            "danger":((83,46,53),(139,76,81),(255,199,188))
        }
        fill,edge,ink=palette.get(style,palette["normal"])
        pygame.draw.rect(self.canvas,fill,rect,border_radius=9)
        pygame.draw.rect(self.canvas,edge,rect,1,border_radius=9)
        self.text(label,rect.centerx,rect.centery,11 if small else 13,ink,True)
        self.buttons.append((rect,action))

    def notice(self, msg, seconds=3, error=False):
        self.toast=str(msg)
        self.toast_until=time.monotonic()+seconds
        self.toast_error=error

    def set_notice(self,msg,error=False):
        self.notice_text=str(msg)
        self.notice_error=error

    def start_task(self, name, function):
        if name in self.tasks:
            return False
        self.tasks.add(name)
        def run():
            try:
                self.queue.put((name,function(),None))
            except Exception as exc:
                self.queue.put((name,None,str(exc)))
        threading.Thread(target=run,daemon=True).start()
        return True

    def submit_auth(self):
        name=self.username_input.strip()
        password=self.password_input
        if not name or not password:
            self.set_notice("아이디와 비밀번호를 입력해 줘.",True);return
        if self.auth_mode=="signup" and not 3<=len(name)<=18:
            self.set_notice("회원가입 아이디는 3~18자로 입력해 줘.",True);return
        if self.auth_mode=="signup" and len(password)<4:
            self.set_notice("비밀번호는 4자 이상이어야 해.",True);return
        mode=self.auth_mode
        self.set_notice("서버에 연결하고 있어…")
        def work():
            endpoint="/api/register" if mode=="signup" else "/api/login"
            auth=api_request(endpoint,"POST",{"username":name,"password":password})
            token=auth.get("token","")
            save=api_request("/api/save",token=token).get("save",{})
            return (auth,save if isinstance(save,dict) else {})
        if not self.start_task("auth",work):
            self.set_notice("이미 서버에 연결하고 있어.",True)

    def poll_tasks(self):
        while not self.queue.empty():
            name,result,error=self.queue.get()
            self.tasks.discard(name)
            if name=="auth":
                if error:
                    self.set_notice(error,True)
                    continue
                auth,save=result
                self.token=auth.get("token","")
                self.current_user=auth.get("username",self.username_input.strip())
                self.nickname=auth.get("nickname",self.current_user)
                self.role=auth.get("role","player")
                self.data=default_save()
                self.data.update(save)
                # Drop obsolete pet-raising fields from older saves.
                for old_field in ("taehyun_hunger","taehyun_happiness","taehyun_level","taehyun_exp","taehyun_feed_count","taehyun_play_count"):
                    self.data.pop(old_field,None)
                cleared=self.data.get("cleared_zones",[])
                if not isinstance(cleared,list) or len(cleared)!=len(ZONES):
                    self.data["cleared_zones"]=[False]*len(ZONES)
                    self.data["player_x"]=160.0
                    self.data["boss_kills"]=0
                    self.data["game_clear"]=False
                    self.data["checkpoint_zone"]=0
                self.data["skill_levels"]=dict({"power":0,"vitality":0},**(self.data.get("skill_levels") or {}))
                self.data["player_x"]=clamp(float(self.data.get("player_x",160)),40,WORLD_W-40)
                today=date.today().isoformat()
                if self.data.get("daily_claim")!=today:
                    self.data["gold"]=int(self.data.get("gold",0))+100+int(self.data.get("level",1))*10
                    self.data["potions"]=int(self.data.get("potions",3))+2
                    self.data["daily_claim"]=today
                    self.save()
                    self.notice("접속 보상! 골드와 물약을 받았어.",4)
                self.view="game"
                self.save_status="온라인 연결됨"
                if self.data.get("game_clear"):self.notice("천상 키우기 엔딩을 이어서 볼 수 있어!",4)
                if self.role=="admin":self.load_admin()
            elif name=="save":
                self.save_status="온라인 저장 완료"
                if self.save_again:
                    self.save_again=False
                    self.save()
            elif name=="admin":
                self.admin_users=result or []
                self.admin_loading=False
            elif name=="admin_action":
                self.admin_users=result or []
                self.admin_loading=False
                self.notice("관리자 작업을 완료했어.")
            elif name=="admin_error":
                self.admin_loading=False
                self.notice(error or "관리자 작업에 실패했어.",3,True)
            elif name=="save_error":
                self.save_status="저장 실패 · 연결 확인"
                if self.save_again:
                    self.save_again=False
                    self.save()

    def save(self):
        if not self.token:return
        if not self.save_lock.acquire(blocking=False):
            self.save_again=True
            return
        snapshot=copy.deepcopy(self.data);token=self.token
        self.save_status="저장 중…"
        self.last_save=time.monotonic()
        def work():
            try:
                api_request("/api/save","PUT",snapshot,token=token,timeout=5)
                self.queue.put(("save",True,None))
            except Exception as exc:
                self.queue.put(("save_error",None,str(exc)))
            finally:
                self.save_lock.release()
        threading.Thread(target=work,daemon=True).start()

    def load_admin(self):
        if self.role!="admin" or self.admin_loading:return
        self.admin_loading=True
        token=self.token
        def work():
            return api_request("/api/admin/users",token=token).get("users",[])
        if not self.start_task("admin",work):self.admin_loading=False

    def admin_action(self,username,action):
        if self.admin_loading:return
        self.admin_loading=True
        token=self.token
        def work():
            return api_request("/api/admin/user/"+urllib.parse.quote(username,safe="")+"/action","POST",{"action":action},token=token).get("users",[])
        def run():
            try:self.queue.put(("admin_action",work(),None))
            except Exception as exc:self.queue.put(("admin_error",None,str(exc)))
        threading.Thread(target=run,daemon=True).start()

    @property
    def zone_i(self):
        return max(0,min(len(ZONES)-1,int(max(0,self.data.get("player_x",160))//ZONE_LENGTH)))

    @property
    def zone(self):
        return ZONES[self.zone_i]

    @property
    def total_attack(self):
        return int(self.data.get("attack",10))+int(self.data.get("weapon_level",0))*5+len(self.data.get("pets",[]))*2+int(self.data.get("skill_levels",{}).get("power",0))*3

    def zone_available(self,i):
        return 0<=i<len(ZONES) and int(self.data.get("level",1))>=ZONES[i]["need"] and all(self.data["cleared_zones"][j] for j in range(i))

    def gain_exp(self,amount):
        self.data["exp"]=int(self.data.get("exp",0))+int(amount)
        gained=0
        while self.data["exp"]>=int(self.data["level"])*30:
            self.data["exp"]-=int(self.data["level"])*30
            self.data["level"]+=1
            self.data["attack"]+=3
            self.data["max_hp"]+=12
            self.data["hp"]=self.data["max_hp"]
            self.data["skill_points"]=int(self.data.get("skill_points",0))+1
            gained+=1
        if gained:self.notice("레벨 업! Lv.%s · 공격력 상승"%self.data["level"],3)
        self.save()

    def spawn_mob(self,i):
        if len(self.enemies)>=4 or any(e["boss"] for e in self.enemies):return
        z=ZONES[i];left=i*ZONE_LENGTH+120;right=(i+1)*ZONE_LENGTH-380
        x=clamp(self.data["player_x"]+random.choice([-1,1])*random.randint(140,250),left,right)
        name=random.choice(z["mobs"]);hp=24+i*17+max(0,self.data["level"]-z["need"])*3
        self.enemies.append({"name":name,"x":float(x),"hp":hp,"max_hp":hp,"damage":max(3,5+i*2+self.data["level"]//5),"speed":25+i*1.1,"exp":14+i*3+self.data["level"]*2,"gold":12+i*3+self.data["level"],"boss":False,"zone_i":i,"hitclock":random.uniform(.2,.8),"flash":0.0,"color":random.choice([(118,184,126),(219,149,108),(188,151,108),(118,165,186),(173,137,193)])})

    def spawn_boss(self,i):
        if self.data["cleared_zones"][i] or any(e["boss"] for e in self.enemies):return
        z=ZONES[i];cols=[(79,159,138),(189,101,93),(114,184,201),(147,132,196),(164,156,131),(215,91,68),(75,158,174),(121,168,216),(107,131,191),(115,141,100),(132,126,226),(98,81,131),(189,71,100)]
        self.enemies.clear()
        self.enemies.append({"name":z["boss"],"x":float((i+1)*ZONE_LENGTH-245),"hp":z["hp"],"max_hp":z["hp"],"damage":z["damage"],"speed":18+i*1.3,"exp":z["exp"],"gold":z["gold"],"boss":True,"zone_i":i,"hitclock":.7,"flash":0.0,"color":cols[i]})
        self.notice("지역 수호자 등장: "+z["boss"]+"!",4)

    def attack(self,mult=1.0):
        if self.view!="game" or self.data.get("game_clear") or self.attack_cd>0:return
        self.attack_cd=.34;self.attack_flash=.22
        nearby=sorted([e for e in self.enemies if abs(e["x"]-self.data["player_x"])<=(240 if mult>1 else 155)],key=lambda e:abs(e["x"]-self.data["player_x"]))
        if not nearby:self.notice("공격 범위 안에 적이 없어.",1.2);return
        for e in (nearby[:3] if mult>1 else nearby[:1]):
            dmg=max(1,int(self.total_attack*mult*random.uniform(.86,1.16)))
            e["hp"]-=dmg;e["flash"]=.17;self.effects.append({"x":e["x"],"text":"-"+str(dmg),"life":.7})
            if e["hp"]<=0:self.defeat(e)
        if mult>1:self.notice("강타!",1)

    def defeat(self,e):
        if e not in self.enemies:return
        self.enemies.remove(e)
        self.data["gold"]+=int(e["gold"])
        self.data["kills"]=int(self.data.get("kills",0))+1
        if e["boss"]:
            i=e["zone_i"]
            self.data["boss_kills"]=int(self.data.get("boss_kills",0))+1
            self.data["cleared_zones"][i]=True
            self.data["checkpoint_zone"]=min(len(ZONES)-1,i+1)
            self.data["potions"]+=2
            self.data["crystals"]+=random.randint(2,4)+i
            self.gain_exp(e["exp"])
            pets=self.data.get("pets",[])
            if self.data["boss_kills"]==1 and "꼬마 슬라임" not in pets:pets.append("꼬마 슬라임")
            if self.data["boss_kills"]==3 and "불꽃 여우" not in pets:pets.append("불꽃 여우")
            if i<len(ZONES)-1:
                self.data["gold"]+=150+i*25
                npc=NPCS[i]
                self.notice(e["name"]+" 격파! "+npc+"에게서 보상을 받았어!",5)
            else:
                self.data["game_clear"]=True
                self.notice("최종 보스 격파! 천상 키우기 완료!",6)
            self.save()
        else:
            self.gain_exp(e["exp"])
            if self.data["kills"]%8==0:self.data["potions"]+=1
        self.save()

    def potion(self):
        if self.data["potions"]<=0:self.notice("물약이 없어. 상점에서 구매할 수 있어.");return
        if self.data["hp"]>=self.data["max_hp"]:self.notice("체력이 이미 가득해.");return
        self.data["potions"]-=1
        self.data["hp"]=min(self.data["max_hp"],self.data["hp"]+max(40,self.data["max_hp"]//2))
        self.notice("회복 물약을 사용했어.")
        self.save()

    def action(self,a):
        if isinstance(a,tuple) and a[0]=="admin_action":self.admin_action(a[1],a[2]);return
        if a=="login":self.auth_mode="login";self.set_notice("기존 계정으로 로그인해 줘.")
        elif a=="signup":self.auth_mode="signup";self.set_notice("회원가입은 아이디 3~18자, 비밀번호 4자 이상이야.")
        elif a=="submit":self.submit_auth()
        elif a=="logout":
            self.save()
            self.token="";self.current_user="";self.role="player";self.username_input="";self.password_input="";self.view="login";self.set_notice("로그아웃했어.")
        elif a=="attack":self.attack(1)
        elif a=="skill":self.attack(1.8)
        elif a=="potion":self.potion()
        elif a=="save":self.save();self.notice("저장 요청을 보냈어.")
        elif a=="admin":self.view="admin";self.load_admin()
        elif a=="admin_back":self.view="game"
        elif a=="admin_refresh":self.load_admin()
        elif a=="admin_prev":self.admin_offset=max(0,self.admin_offset-4)
        elif a=="admin_next":self.admin_offset=min(max(0,len(self.admin_users)-4),self.admin_offset+4)
        elif a=="buy_potion":
            if self.data["gold"]<40:self.notice("골드 40 G가 필요해.")
            else:self.data["gold"]-=40;self.data["potions"]+=1;self.notice("물약을 구매했어.");self.save()
        elif a=="weapon":
            if self.data["gold"]<100:self.notice("골드 100 G가 필요해.")
            else:self.data["gold"]-=100;self.data["weapon_level"]+=1;self.notice("무기 강화 완료! 공격력 +5");self.save()
        elif a=="armor":
            if self.data["gold"]<100:self.notice("골드 100 G가 필요해.")
            else:self.data["gold"]-=100;self.data["armor_level"]+=1;self.notice("방어구 강화 완료!");self.save()
        elif a=="rebirth":
            old_gold=int(self.data.get("gold",0))
            old_daily=self.data.get("daily_claim","")
            old_rebirths=int(self.data.get("rebirth_count",0))+1
            self.data=default_save()
            self.data["gold"]=old_gold
            self.data["daily_claim"]=old_daily
            self.data["rebirth_count"]=old_rebirths
            self.data["attack"]=10+(old_rebirths-1)*2
            self.enemies.clear()
            self.view="game"
            self.notice("새 모험을 시작했어! 환생 보너스가 적용됐어.",4)
            self.save()


    def jump(self):
        if self.on_ground and self.view=="game" and not self.data.get("game_clear"):
            self.jump_v=370;self.on_ground=False

    def update(self,dt):
        self.poll_tasks()
        now=time.monotonic()
        if self.view!="game":return
        if now-self.last_save>20:self.save()
        if self.data.get("game_clear"):
            return
        self.attack_cd=max(0,self.attack_cd-dt);self.attack_flash=max(0,self.attack_flash-dt);self.invulnerable=max(0,self.invulnerable-dt)
        if "left" in self.pointer_held or pygame.K_LEFT in self.keys or pygame.K_a in self.keys:self.data["player_x"]-=205*dt;self.facing=-1
        if "right" in self.pointer_held or pygame.K_RIGHT in self.keys or pygame.K_d in self.keys:self.data["player_x"]+=205*dt;self.facing=1
        self.data["player_x"]=clamp(self.data["player_x"],35,WORLD_W-35)
        zi=self.zone_i
        if not self.zone_available(zi):self.data["player_x"]=min(self.data["player_x"],max(35,zi*ZONE_LENGTH-40))
        zi=self.zone_i;end=(zi+1)*ZONE_LENGTH
        if not self.data["cleared_zones"][zi] and self.data["player_x"]>=end-380:
            self.data["player_x"]=min(self.data["player_x"],end-300);self.spawn_boss(zi)
        self.spawn_timer+=dt
        if self.spawn_timer>1.8 and len([e for e in self.enemies if not e["boss"]])<3 and not any(e["boss"] for e in self.enemies) and not self.data["cleared_zones"][zi]:
            self.spawn_timer=0;self.spawn_mob(zi)
        if (pygame.K_f in self.keys or pygame.K_j in self.keys) and self.attack_cd<=0:self.attack()
        if pygame.K_1 in self.keys and self.attack_cd<=0:self.attack(1.8)
        if not self.on_ground:
            self.jump_v-=930*dt;self.player_y+=self.jump_v*dt
            if self.player_y<=0:self.player_y=0;self.jump_v=0;self.on_ground=True
        for e in list(self.enemies):
            e["flash"]=max(0,e["flash"]-dt)
            dx=self.data["player_x"]-e["x"]
            if abs(dx)>54:e["x"]+=math.copysign(min(abs(dx),e["speed"]*dt),dx)
            else:
                e["hitclock"]-=dt
                if e["hitclock"]<=0:
                    e["hitclock"]=.9 if e["boss"] else 1.1
                    if self.invulnerable<=0:
                        damage=max(1,e["damage"]-int(self.data.get("armor_level",0))*2-len(self.data.get("pets",[])))
                        self.data["hp"]-=damage;self.invulnerable=.55;self.notice(e["name"]+"의 공격! -"+str(damage),1.1)
                        if self.data["hp"]<=0:
                            self.data["hp"]=max(1,int(self.data["max_hp"]*.55));self.data["player_x"]=max(40,int(self.data.get("checkpoint_zone",0))*ZONE_LENGTH+100);self.player_y=0;self.jump_v=0;self.on_ground=True;self.enemies=[m for m in self.enemies if not m["boss"]];self.notice("체크포인트에서 다시 일어났어.",3);self.save();break
        for fx in self.effects:fx["life"]-=dt
        self.effects=[fx for fx in self.effects if fx["life"]>0]

    def draw_bg(self,z,camera):
        c=self.canvas
        bottom=mix(z["sky"],(230,222,199),.74)
        for y in range(0,H,8):pygame.draw.rect(c,mix(z["sky"],bottom,y/H),(0,y,W,8))
        for row in range(3):
            pts=[(0,370)]
            for x in range(-20,W+30,20):
                yy=335-row*22-math.sin((x+camera*(.09+row*.035))/(90+row*17))*(22+row*4)-math.sin((x+camera*.12+row*91)/58)*9
                pts.append((x,int(yy)))
            pts.extend([(W,H),(0,H)])
            pygame.draw.polygon(c,mix(z["hill"],z["sky"],.2+row*.13),pts)
        ground=475
        pygame.draw.rect(c,z["ground"],(0,ground,W,H-ground))
        pygame.draw.line(c,mix(z["ground"],(231,220,177),.45),(0,ground),(W,ground),3)
        for j in range(20):
            x=int((j*77-camera*.55)%(W+30));pygame.draw.circle(c,mix(z["ground"],(35,65,44),.22),(x,ground+10+(j%4)*9),2+j%3)
        for i in range(len(ZONES)):
            x=i*ZONE_LENGTH-camera
            if -60<=x<=W+60:
                pygame.draw.rect(c,(25,38,48),(int(x+7),ground-35,38,22),border_radius=5)
                self.text(str(i+1).zfill(2),x+26,ground-24,10,(244,222,174),True)

    def draw_char(self,x,ground,color,scale=1,blink=False):
        c=self.canvas;r=max(2,int(10*scale))
        pygame.draw.ellipse(c,(35,47,44),(int(x-20*scale),int(ground-3*scale),int(40*scale),int(7*scale)))
        pygame.draw.rect(c,(246,232,194) if blink else color,(int(x-12*scale),int(ground-39*scale),int(24*scale),int(25*scale)),border_radius=max(2,int(5*scale)))
        pygame.draw.circle(c,(237,204,164),(int(x),int(ground-46*scale)),r+1)
        pygame.draw.arc(c,(37,47,52),(int(x-r),int(ground-58*scale),r*2,int(r*1.4)),math.pi,2*math.pi,max(2,int(3*scale)))
        pygame.draw.circle(c,(37,46,51),(int(x-4*scale),int(ground-47*scale)),max(1,int(1.7*scale)))
        pygame.draw.circle(c,(37,46,51),(int(x+4*scale),int(ground-47*scale)),max(1,int(1.7*scale)))
        pygame.draw.rect(c,(52,61,66),(int(x-8*scale),int(ground-15*scale),int(6*scale),int(14*scale)),border_radius=2)
        pygame.draw.rect(c,(52,61,66),(int(x+2*scale),int(ground-15*scale),int(6*scale),int(14*scale)),border_radius=2)

    def draw_enemy(self,e,camera):
        x=e["x"]-camera
        if x<-85 or x>W+85:return
        ground=475;r=18*(1.4 if e["boss"] else 1)
        col=(250,240,225) if e["flash"]>0 else e["color"]
        if e["boss"]:
            pts=[(int(x-r),ground-4),(int(x-r-7),ground-28),(int(x-5),ground-59),(int(x+r+7),ground-31),(int(x+r),ground-4)]
            pygame.draw.polygon(self.canvas,col,pts);pygame.draw.polygon(self.canvas,(35,43,52),pts,2)
        else:
            pygame.draw.ellipse(self.canvas,col,(int(x-r),int(ground-r),int(r*2),int(r*1.5)))
            pygame.draw.ellipse(self.canvas,(48,53,58),(int(x-r),int(ground-r),int(r*2),int(r*1.5)),2)
        pygame.draw.circle(self.canvas,(32,40,45),(int(x-5),int(ground-17)),2)
        pygame.draw.circle(self.canvas,(32,40,45),(int(x+5),int(ground-17)),2)
        by=int(ground-r-18);pygame.draw.rect(self.canvas,(32,37,43),(int(x-35),by,70,6),border_radius=3)
        pygame.draw.rect(self.canvas,(222,117,106) if e["boss"] else (155,197,134),(int(x-35),by,int(70*max(0,e["hp"]/e["max_hp"])),6),border_radius=3)
        self.text(e["name"],x,by-10,11 if e["boss"] else 10,(249,239,218),True)

    def draw_hud(self):
        d=self.data;z=self.zone
        self.panel((12,12,212,68),(25,36,48),(75,88,99),10)
        self.text(z["name"],23,21,14,(245,224,179))
        self.text("Lv.%s · ATK %s"%(d["level"],self.total_attack),23,45,11,(215,222,227))
        self.panel((232,12,390,68),(25,36,48),(75,88,99),10)
        self.text("HP %s / %s"%(max(0,int(d["hp"])),d["max_hp"]),244,21,12)
        pygame.draw.rect(self.canvas,(13,20,28),(244,45,174,9),border_radius=4)
        pygame.draw.rect(self.canvas,(206,117,109),(244,45,int(174*clamp(d["hp"]/max(1,d["max_hp"]),0,1)),9),border_radius=4)
        self.text("EXP %s/%s"%(d["exp"],d["level"]*30),430,43,11,(217,205,177))
        self.panel((642,12,306,68),(25,36,48),(75,88,99),10)
        self.text("%s G"%d["gold"],655,20,14,(246,219,155))
        self.text("물약 %s · 수정 %s · 수호자 %s/13"%(d["potions"],d["crystals"],sum(d["cleared_zones"])),655,46,10,(208,218,225))

    def draw_game(self):
        c=self.canvas
        if self.data.get("game_clear"):self.draw_victory();return
        camera=clamp(self.data["player_x"]-W*.36,0,max(0,WORLD_W-W));self.camera_x=camera
        self.draw_bg(self.zone,camera)
        for e in self.enemies:self.draw_enemy(e,camera)
        px=self.data["player_x"]-camera
        self.draw_char(px,475-self.player_y,(220,183,112),1,self.invulnerable>0)
        if self.attack_flash>0:
            box=(int(px-8),int(419-self.player_y),64,56)
            pygame.draw.arc(c,(255,239,196),box,-.85 if self.facing==1 else 2.25,.85 if self.facing==1 else 4,4)
        for fx in self.effects:self.text(fx["text"],fx["x"]-camera,385-(.7-fx["life"])*35,13,(255,239,181),True)
        self.draw_hud()
        if self.role=="admin":self.button((811,91,137,29),"관리자 메뉴","admin","quiet",True)
        self.button((14,476,78,48),"◀ 이동","hold_left")
        self.button((98,476,78,48),"이동 ▶","hold_right")
        self.button((182,476,78,48),"⬆ 점프","jump")
        self.button((649,476,91,48),"공격 (F)","attack","primary")
        self.button((746,476,91,48),"강타 (1)","skill")
        self.button((843,476,103,48),"물약 (H)","potion")
        self.button((15,91,89,28),"저장","save","quiet",True)
        self.button((111,91,89,28),"로그아웃","logout","quiet",True)
        if time.monotonic()<self.toast_until:
            edge=(157,87,80) if self.toast_error else (85,106,117)
            pygame.draw.rect(c,(30,42,51),(232,91,490,34),border_radius=9)
            pygame.draw.rect(c,edge,(232,91,490,34),1,border_radius=9)
            self.text(self.toast,477,108,11,(250,229,193),True)
        self.text("PC: A/D 이동 · Space 점프 · F 공격 · 1 강타 · H 물약",480,455,10,(194,204,212),True)
        # The small buttons keep upgrades accessible without obscuring the playfield.
        self.button((270,476,112,48),"물약 40 G","buy_potion","quiet",True)
        self.button((390,476,112,48),"무기 강화","weapon","quiet",True)
        self.button((510,476,112,48),"방어 강화","armor","quiet",True)

    def draw_victory(self):
        c=self.canvas
        self.draw_bg(ZONES[-1],self.camera_x)
        pygame.draw.rect(c,(20,29,40),(120,58,720,390),border_radius=20)
        pygame.draw.rect(c,(85,103,119),(120,58,720,390),2,border_radius=20)
        self.text("CHUNSANG ADVENTURE",480,100,11,(222,190,127),True)
        self.text("천상 키우기",480,143,30,(247,229,190),True)
        self.text("최종 보스 격파!",480,194,23,(236,239,233),True)
        self.text("13개 지역의 모험을 모두 완료했어.",480,235,14,(184,199,210),True)
        self.text("레벨 %s  ·  처치 %s  ·  골드 %s G"%(self.data.get("level",1),self.data.get("kills",0),self.data.get("gold",0)),480,270,13,(224,204,160),True)
        self.button((190,326,250,52),"다시 모험하기","rebirth","primary")
        self.button((458,326,125,52),"지금 저장","save","quiet")
        self.button((593,326,170,52),"로그아웃","logout","quiet")
        if self.role=="admin":
            self.button((783,70,40,32),"⚙","admin","quiet",True)
        if time.monotonic()<self.toast_until:
            edge=(157,87,80) if self.toast_error else (85,106,117)
            pygame.draw.rect(c,(30,42,51),(235,404,490,32),border_radius=9)
            pygame.draw.rect(c,edge,(235,404,490,32),1,border_radius=9)
            self.text(self.toast,480,420,11,(250,229,193),True)

    def draw_admin(self):
        c=self.canvas;c.fill((21,27,37));self.panel((20,18,920,504),(30,39,52),(61,75,91),16)
        self.text("관리자 · 계정 관리",42,37,24,(242,220,173));self.text("골드, 레벨, 아이템, 이용 제한을 관리해.",42,72,12,(171,185,197))
        self.button((718,35,96,32),"새로고침","admin_refresh","quiet",True);self.button((822,35,94,32),"게임으로","admin_back","normal",True)
        if self.admin_loading:self.text("계정 목록을 불러오는 중…",480,145,15,(224,229,230),True)
        elif not self.admin_users:self.text("계정이 없거나 관리자 권한이 없어.",480,145,13,(214,218,222),True)
        else:
            for idx,u in enumerate(self.admin_users[self.admin_offset:self.admin_offset+4]):
                y=102+idx*91;self.panel((38,y,884,78),(35,45,58),(58,72,87),10)
                name=u.get("username","?");save=u.get("save") or {}
                self.text(name+(" · 관리자" if u.get("role")=="admin" else ""),52,y+10,14,(238,239,232))
                self.text(("이용 제한" if u.get("banned") else "정상")+" · Lv.%s · %s G"%(save.get("level",1),save.get("gold",0)),52,y+37,11,(161,178,192))
                if u.get("role")!="admin":
                    self.button((432,y+15,101,42),"골드 +1000",("admin_action",name,"add_gold"),"normal",True)
                    self.button((540,y+15,95,42),"레벨 +5",("admin_action",name,"add_levels"),"normal",True)
                    self.button((642,y+15,95,42),"아이템 +",("admin_action",name,"add_items"),"normal",True)
                    self.button((746,y+15,158,42),"정지 해제" if u.get("banned") else "계정 정지",("admin_action",name,"toggle_ban"),"danger" if not u.get("banned") else "normal",True)
        self.button((38,465,100,34),"이전","admin_prev","quiet",True);self.button((147,465,100,34),"다음","admin_next","quiet",True)
        self.text("%s개 계정 · %s-%s"%(len(self.admin_users),self.admin_offset+1,min(self.admin_offset+4,len(self.admin_users))),270,477,11,(163,178,193))

    def draw_login(self):
        c=self.canvas;c.fill((21,27,37));pygame.draw.ellipse(c,(31,48,59),(-190,-220,650,500));pygame.draw.ellipse(c,(33,44,51),(610,340,510,360))
        self.panel((240,36,480,468),(31,40,53),(58,73,90),17)
        self.text("✦",480,83,28,(225,189,116),True);self.text("천상 키우기",480,124,28,(246,224,179),True);self.text("13개 지역을 돌파하고 최종 보스에 도전하자",480,154,12,(167,184,195),True)
        self.button((276,178,197,35),"로그인","login","primary" if self.auth_mode=="login" else "quiet")
        self.button((487,178,197,35),"회원가입","signup","primary" if self.auth_mode=="signup" else "quiet")
        self.text("아이디",278,230,11,(202,211,219));self.text("비밀번호",278,304,11,(202,211,219))
        self.fields={"username":pygame.Rect(276,248,408,40),"password":pygame.Rect(276,322,408,40)}
        for field,rect,value in [("username",self.fields["username"],self.username_input),("password",self.fields["password"],"●"*len(self.password_input))]:
            active=field==self.active_field
            pygame.draw.rect(c,(18,25,34),rect,border_radius=8);pygame.draw.rect(c,(206,171,104) if active else (60,73,87),rect,2 if active else 1,border_radius=8)
            self.text(value if value else ("아이디 입력" if field=="username" else "비밀번호 입력"),rect.x+12,rect.y+12,13,(237,239,233) if value else (119,134,147))
        self.button((276,382,408,43),"로그인하고 시작" if self.auth_mode=="login" else "계정 만들기","submit","primary")
        lines=self.wrap_text(getattr(self,"notice_text",self.notice),405,11)
        note_color=(255,166,155) if self.notice_error else (163,185,183)
        for i,line in enumerate(lines[:2]):self.text(line,480,441+i*15,11,note_color,True)
        self.text("온라인 계정 · 기기 간 진행 상황 저장",480,491,10,(113,132,147),True)

    def wrap_text(self,value,width,size):
        lines=[];line=""
        for word in str(value).split():
            test=(line+" "+word).strip()
            if self.font(size).size(test)[0]<=width:line=test
            else:
                if line:lines.append(line)
                line=word
        if line:lines.append(line)
        return lines or [""]

    def click(self,pos):
        if self.view=="login":
            for field,rect in self.fields.items():
                if rect.collidepoint(pos):
                    self.active_field=field
                    try:pygame.key.start_text_input()
                    except Exception:pass
                    return
        for rect,action in reversed(self.buttons):
            if rect.collidepoint(pos):
                if action=="hold_left":self.pointer_held.add("left")
                elif action=="hold_right":self.pointer_held.add("right")
                elif action=="jump":self.jump()
                else:self.action(action)
                return

    def event(self,e):
        if e.type==pygame.QUIT:self.close();return
        if e.type==pygame.VIDEORESIZE and not self.android:
            self.screen=pygame.display.set_mode(e.size,pygame.RESIZABLE);return
        if e.type==pygame.KEYDOWN:
            if self.view=="login":
                if e.key==pygame.K_TAB:self.active_field="password" if self.active_field=="username" else "username"
                elif e.key==pygame.K_BACKSPACE:
                    if self.active_field=="username":self.username_input=self.username_input[:-1]
                    else:self.password_input=self.password_input[:-1]
                elif e.key==pygame.K_RETURN:
                    if self.active_field=="username":self.active_field="password"
                    else:self.submit_auth()
                elif e.key==pygame.K_ESCAPE:self.close()
            else:
                self.keys.add(e.key)
                if e.key==pygame.K_SPACE:self.jump()
                elif e.key in (pygame.K_f,pygame.K_j):self.attack()
                elif e.key==pygame.K_1:self.attack(1.8)
                elif e.key==pygame.K_h:self.potion()
                elif e.key==pygame.K_ESCAPE and self.view=="admin":self.view="game"
                elif e.key==pygame.K_F5 and self.role=="admin":self.load_admin()
        elif e.type==pygame.KEYUP:self.keys.discard(e.key)
        elif e.type==pygame.TEXTINPUT and self.view=="login":
            if self.active_field=="username" and len(self.username_input)<18:self.username_input+=e.text
            elif self.active_field=="password" and len(self.password_input)<72:self.password_input+=e.text
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            self.click((int(e.pos[0]*W/max(1,self.screen.get_width())),int(e.pos[1]*H/max(1,self.screen.get_height()))))
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:self.pointer_held.clear()
        elif e.type==pygame.FINGERDOWN:self.click((int(e.x*W),int(e.y*H)))
        elif e.type in (pygame.FINGERUP,pygame.FINGERCANCEL):self.pointer_held.clear()

    def close(self):
        if self.token and self.view in ("game","admin"):
            try:api_request("/api/save","PUT",copy.deepcopy(self.data),self.token,timeout=1.2)
            except Exception:pass
        self.running=False;pygame.quit()

    def run(self):
        while self.running:
            dt=min(.05,self.clock.tick(FPS)/1000.0)
            for e in pygame.event.get():
                self.event(e)
                if not self.running:break
            if not self.running:break
            self.update(dt)
            self.buttons=[]
            if self.view=="login":self.draw_login()
            elif self.view=="admin":self.draw_admin()
            else:self.draw_game()
            if self.view=="game":
                self.text(self.save_status,944,535,9,(141,157,170))
            sw,sh=self.screen.get_size()
            self.screen.blit(pygame.transform.scale(self.canvas,(max(1,sw),max(1,sh))),(0,0))
            pygame.display.flip()
        return 0


def main():
    return ChunsangGame().run()


if __name__=="__main__":
    main()
