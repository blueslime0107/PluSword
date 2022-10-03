
from glob import glob
from json import load
import math
from os import curdir
import random
from select import select
import time
from re import A
from turtle import down
from cv2 import transform
from numpy import block, full

import pygame
from pip import main
from pygame.locals import *

#region defaltGameSet
pygame.init()
pygame.mixer.pre_init(44100,-16,2,512)

pygame.mixer.set_num_channels(64)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

WIDTH = 1080
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH,HEIGHT))
menu_render = pygame.Surface((1020,360), SRCALPHA)
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

clock = pygame.time.Clock()
clock_fps = 60     
TARGET_FPS = 60

fullscreen = False
game_setting = [0,0,100,100]
# 캐릭터(0/1), 난이도(0/1/2), 음악볼륨/100, 효과음볼륨/100, 화면설정(0,1)
#endregion
#region PictureLoad
main_char1 = pygame.image.load('resource\Sprites\mainChar1.png').convert_alpha() 
char1 = pygame.image.load('resource\Sprites\char1.png').convert_alpha()
char2 = pygame.image.load('resource\Sprites\char2.png').convert_alpha()
menu = pygame.image.load('resource\Sprites\Menu.png').convert_alpha()
floor = pygame.image.load('resource\Sprites\Floor.png').convert_alpha()
others = pygame.image.load('resource\Sprites\others.png').convert_alpha()
progress = pygame.image.load('resource\Sprites\Bar.png').convert_alpha()
#endregion
#region PictureCutSave
a_list = []
for i in range (0,64,32):
    for j in range (0,192,32):
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(others, (0,0), Rect(j,i,32,32))
        image = pygame.transform.scale(image,(128,128))
        a_list.append(image)
menu_icon = a_list
a_list = []
for i in range (0,256,128):
    for j in range (0,384,96):
        image = pygame.Surface((96, 128), pygame.SRCALPHA)
        image.blit(main_char1, (0,0), Rect(j,i,96,128))
        a_list.append(image)
spr_mainChar1 = a_list

#endregion
#region FontLoad
menuFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 45)
capitextFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 30)
textFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 25)
numberFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 25)
damageFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 15)
#endregion






def convertImage(surface,x,y,w,h):
    image = pygame.Surface((w, h), pygame.SRCALPHA)
    image.blit(surface, (0,0), Rect(x,y,w,h))
    image = pygame.transform.scale(image,(w*5,h*5))
    return image


class MainItem:
    def __init__(self,num, name, message=[""], icon=pygame.Surface((16,16))):
        self.num = num
        self.name = name
        self.count = 0
        self.message = message
        self.icon = icon
    def active(self):
        global game_setting
        global fullscreen
        global game_player
        global game_start
        global game_lobby
        if(self.num == 0):
            print("Manual")
        if(self.num == 1):
            global player_rect
            global player_tri
            game_player = player_tri if game_player == player_rect else player_rect
        if(self.num == 2):
            gameStart()
        if(self.num == 3):
            gameStart()
        if(self.num == 4):
            gameStart()

        if(self.num == 5):
            game_setting[2] += 5
            if(game_setting[2]>100): game_setting[2] = 100
            self.count = game_setting[2]
        if(self.num == 6):
            game_setting[2] -= 5
            if(game_setting[2]<0): game_setting[2] = 0
            self.count = game_setting[2]
        if(self.num == 7):
            game_setting[3] += 5
            if(game_setting[3]>100): game_setting[3] = 100
            self.count = game_setting[3]
        if(self.num == 8):
            game_setting[3] -= 5
            if(game_setting[3]<0): game_setting[3] = 0
            self.count = game_setting[3]
        if(self.num == 9):          
            setFullScreen()
            self.count = int(fullscreen)

class Stage:
    def __init__(self,num,enemys = []):
        self.num = num
        self.enemys = enemys

class Player:
    def __init__(self,name="",sprite=pygame.Surface((1,1)),health=0,weapon = []):
        self.tag = "Player"
        self.pos = 144
        self.name = name

        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        self.sprite = sprite
        self.health = health
        self.max_health = self.health
        self.weapon = []
        self.item = []
        self.weapon.append(weapon)
        self.behavior = 3

        self.condition = 0
        self.idle1 = convertImage(self.sprite,0,0,32,32)
        self.idle2 = convertImage(self.sprite,32,0,32,32)
        self.icon = convertImage(self.sprite,64,0,32,32)
        self.ready = convertImage(self.sprite,0,32,96,32)
        self.attack = convertImage(self.sprite,0,64,96,32)
        self.damage = convertImage(self.sprite,0,96,96,32)

        self.count = 0
        self.image = self.idle2

        self.moving = False
        self.move_point = self.pos
        self.move_speed = 0

        self.idlespd = 60

    def update(self):
        if(self.pos != self.move_point):
            self.moving = True
            dx = self.move_point - self.pos
            dx /= self.move_speed
            self.pos += dx
            if(abs(self.move_point-self.pos)<2):
                self.moving = False
                self.pos = self.move_point


    def draw(self,screen):
        if(self.condition == 0 or self.condition == 1):
            self.count += 1
            if(self.count % self.idlespd == 0):
                if(self.condition == 0):
                    self.condition = 1
                    self.count = 0
                    self.image = self.idle2
                elif(self.condition == 1):
                    self.condition = 0
                    self.count = 0
                    self.image = self.idle1
                
        pos = 0
        if(self.condition == 0 or self.condition == 1):
            pos = self.pos

        screen.blit(self.image,(pos-self.image.get_rect().centerx,CHARY))

    def setMove(self,pos,spd):
        self.move_point = pos
        self.move_speed = spd

class Weapon:
    def __init__(self,name,id,level=0, message=[""], icon=pygame.Surface((16,16))):
        
        self.id = id 
        self.count = level
        self.damage = 5
        self.exp = 0
        self.max_exp = 0

        self.name = name        
        self.message = message
        self.icon = icon
    def active(self):
        global battleManager
        if(len(battleManager.player_WeaponSlot) < game_player.behavior):
            battleManager.addPlayerWeaponSlot(self)
            progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)

class Item:
    def __init__(self):
        pass

class Enemy:
    def __init__(self,name,sprite,health,weapon = Weapon("",0,0)):
        self.tag = "Enemy"
        self.pos = 906
        self.name = name

        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        self.sprite = sprite
        self.health = health
        self.max_health = self.health
        self.weapon = weapon
        self.item = []

        self.condition = 0
        self.idle1 = convertImage(self.sprite,0,0,32,32)
        self.idle2 = convertImage(self.sprite,32,0,32,32)
        self.icon = convertImage(self.sprite,64,0,32,32)
        self.ready = convertImage(self.sprite,0,32,96,32)
        self.attack = convertImage(self.sprite,0,64,96,32)
        self.damage = convertImage(self.sprite,0,96,96,32)

        self.count = 0
        self.image = self.idle2

        self.moving = False
        self.move_point = self.pos
        self.move_speed = 0

        self.idlespd = 60

    def draw(self,screen):
        if(self.condition == 0 or self.condition == 1):
            self.count += 1
            if(self.count % self.idlespd == 0):
                if(self.condition == 0):
                    self.condition = 1
                    self.count = 0
                    self.image = self.idle2
                elif(self.condition == 1):
                    self.condition = 0
                    self.count = 0
                    self.image = self.idle1
                
        pos = 0
        if(self.condition == 0 or self.condition == 1):
            pos = self.pos

        screen.blit(pygame.transform.flip(self.image,True,False),(pos-self.image.get_rect().centerx,CHARY))

    def update(self):
        if(self.pos != self.move_point):
            self.moving = True
            dx = self.move_point - self.pos
            dx /= self.move_speed
            self.pos += dx
            if(abs(self.move_point-self.pos)<2):
                self.moving = False
                self.pos = self.move_point
    def setMove(self,pos,spd):
        self.move_point = pos
        self.move_speed = spd

class BattleManager:
    def __init__(self):
        self.player = Player()
        self.enemys = []

        self.player_WeaponSlot = []

        self.battle_Chain = []

        self.battleStart = False
        self.battlePre = False
        self.count = 0

    def addPlayerWeaponSlot(self,weapon):
        self.player_WeaponSlot.append(Battle(self.player,weapon))

    def battle(self):
        if not self.battlePre:
            enemy_WeaponSlot = []
            for enemy in self.enemys:
                enemy_WeaponSlot.append(Battle(enemy,enemy.weapon))
            
            self.battle_Chain.extend(self.player_WeaponSlot)
            self.battle_Chain.extend(enemy_WeaponSlot)
            self.battlePre = True

        if(len(self.battle_Chain) > 0):
            self.match()

            













        else:
            self.battleStart = False

    def match(self):
        self.count += 1
        self.battle_Chain[0].update(game_player,self.enemys)


class Battle:
    def __init__(self,attack,weapon):
        self.attack = attack
        self.defend = 0
        self.weapon = weapon
        self.count = 0
    def update(self,player,enemys):
        self.count += 1
        if(self.count == 1):
            if(self.attack.tag == "Player"):
                self.defend = enemys[0]
                self.attack.setMove(540-CENTERDIS,10)
                self.defend.setMove(540+CENTERDIS,10)
            if(self.attack.tag == "Enemy"):
                self.defend = player
                self.attack.setMove(540+CENTERDIS,10)
                self.defend.setMove(540-CENTERDIS,10)
            
        if(self.attack.moving or self.defend.moving):
            return

        a = rndNum(2,9)
        b = rndNum(2,9)
        value = input(str(a) + str(b))
        result = value == a +b
        if(self.attack.tag == "Player"):
            self.defend.health -= self.weapon.damage
                
        if(self.attack.tag == "Enemy"):
            self.attack.health -= self.weapon.damage // 5
        
        del battleManager.battle_Chain[0]
    def moveToCenter(self):
        self.attack.setMove(11,5)

class ProgressBox:
    def __init__(self,var1=0,var2=0,color=(0,0,0)):
        self.var1 = var1
        self.var2 = var2
        self.color = color
    def draw(self, screen, index, blocksize):
        pygame.draw.rect(screen, self.color, Rect(index*blocksize+18,14,blocksize,17), width=0)

class ProgressBar:
    def __init__(self):
        
        self.render = progress
        self.render_img = self.render.copy()
        self.render_list = []
        self.render_max = 3
        self.render_final = []
    def updateProgress(self,lists,max):
        self.render_list = lists
        self.render_final = []
        for index in self.render_list:
            self.render_final.append(ProgressBox(0,0,(255,255,0)))
        self.render_max = max

    def draw(self,screen):
        self.render = progress.copy()
        blocksize = 1044
        blocksize /= self.render_max
        for index in range(0,len(self.render_list)):
            self.render_final[index].draw(self.render,index,blocksize)
        screen.blit(self.render,(0,410))











CHARY = 474
CENTERDIS = 50

keys = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "enter": False,
    "back": False
}

#region 메뉴관련 변수들
mainUpVisual = {
    'text': ''
    ,'message': ['']
    , 'icon': pygame.Surface((32,32))
}
mainDownVisual = {
    'text': ''
    ,'message': ['']
    , 'icon': pygame.Surface((32,32))
}

upperItems = []
downerItems = []

mainCurser = 0
upperCurser = 0
downerCurser = 0

#endregion

battleManager = BattleManager()
progressBar = ProgressBar()
curBattle = Battle("a",Weapon(",",0,0))

player_tri = Player("삼각",spr_mainChar1[0],10,Weapon("플러스검",1))
player_rect = Player("지사",spr_mainChar1[1],9,Weapon("마너스검",2))

game_player = player_tri

game_lobby = True
game_start = False

stage1 = Stage(1,[Enemy("새새색",spr_mainChar1[2],10,Weapon("플러스검",1)),Enemy("배애앰",spr_mainChar1[3],10,Weapon("플러스검",1)),Enemy("배애앰",spr_mainChar1[3],10,Weapon("플러스검",1))])


def play_game():
    #region 기초 변수 초기화

    #region 기본변수
    global screen
    global keys
    global fullscreen
    global mainUpVisual
    global mainDownVisual
    global upperItems
    global downerItems
    global mainCurser
    global upperCurser
    global downerCurser
    global curBattle
    playing = True
    prev_time = 0
    fullscreen = False
    count = 0


    loading = True

    menuAble = False

    curStage = stage1

    battleStart = False
    #endregion

    # region 메인관련변수
    curMenu = "Main"






    render_message = []
    render_icon = pygame.Surface((32,32))

    selectbox = Rect(0,0,0,0)
    #endregion

    # region 게임 자원들 초기화
    listMainUpper = [MainItem(0,"매뉴얼",["수학으로 죽고사는 게임"],menu_icon[2]),MainItem(1,"캐릭터 설정",["수학으로 죽고사는 게임"],menu_icon[3]),\
        MainItem(2,"쉬움",["수학으로 죽고사는 게임"],menu_icon[4]),MainItem(3,"보통",["수학으로 죽고사는 게임"],menu_icon[5]),MainItem(4,"어려움",["수학으로 죽고사는 게임"],menu_icon[6])]
    listMainDowner = [MainItem(5,"배경음 ▲",["수학으로 죽고사는 게임"],menu_icon[7]),MainItem(6,"배경음 ▼",["수학으로 죽고사는 게임"],menu_icon[8]),\
        MainItem(7,"효과음 ▲",["수학으로 죽고사는 게임"],menu_icon[9]),MainItem(8,"효과음 ▼",["수학으로 죽고사는 게임"],menu_icon[10]),MainItem(9,"화면설정",["수학으로 죽고사는 게임"],menu_icon[11])]
    mainUpVisual["text"] = "게임"
    mainUpVisual["message"] = ["플러스워드","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"]
    mainUpVisual["icon"] = menu_icon[0]
    mainDownVisual["text"] = "설정"
    mainDownVisual["message"] = ["게임설정","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"]
    mainDownVisual["icon"] = menu_icon[1]
    upperItems = listMainUpper
    downerItems = listMainDowner
    
    render_message = mainUpVisual["message"]
    render_icon = menu_icon[0]

    menuAble = True
    #endregion

    #endregion
    while(playing):

        #region 게임의 기초,메뉴 조작
        clock.tick(clock_fps)
        now = time.time()        
        dt = (now-prev_time)*TARGET_FPS        
        prev_time = now

        keys["up"] = False
        keys["down"] = False
        keys["left"] = False
        keys["right"] = False
        keys["enter"] = False
        keys["back"] = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 게임끄기
                playing = False
            if event.type == pygame.KEYDOWN: 
                
                keys["up"] = event.key == pygame.K_KP8
                keys["down"] = event.key == pygame.K_KP5
                keys["left"] = event.key == pygame.K_KP4 
                keys["right"] = event.key == pygame.K_KP6  
                keys["enter"] = event.key == pygame.K_KP_ENTER
                keys["back"] = event.key == pygame.K_KP_PERIOD
                if event.key == K_F4: setFullScreen()
            # else:
            #     keys["up"] = False
            #     keys["down"] = False
            #     keys["left"] = False
            #     keys["right"] = False
            #     keys["enter"] = False
            #     keys["back"] = False

                



        if(menuAble):
            if curMenu == "Upper":
                if keys["left"]:
                    curMenu = "Main"
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                if keys["right"]:
                    upperItems[upperCurser].active() # 아이템 발동
                if keys["up"]:
                    upperCurser -= 1
                    if upperCurser < 0: upperCurser = len(upperItems)-1
                    render_message = upperItems[upperCurser].message
                    render_icon = upperItems[upperCurser].icon
                if keys["down"]:
                    upperCurser += 1
                    if upperCurser >= len(upperItems): upperCurser = 0
                    render_message = upperItems[upperCurser].message
                    render_icon = upperItems[upperCurser].icon
            if curMenu == "Downer":
                if keys["left"]:
                    curMenu = "Main"
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                if keys["right"]:
                    downerItems[downerCurser].active() # 아이템 발동
                    
                if keys["up"]:
                    downerCurser -= 1
                    if downerCurser < 0: downerCurser = len(downerItems)-1
                    render_message = downerItems[downerCurser].message
                    render_icon = downerItems[downerCurser].icon
                if keys["down"]:
                    downerCurser += 1
                    if downerCurser >= len(downerItems): downerCurser = 0
                    render_message = downerItems[downerCurser].message
                    render_icon = downerItems[downerCurser].icon
            if curMenu == "Main":
                if keys["right"]:
                    if(mainCurser == 0 and len(upperItems) > 0):
                        curMenu = "Upper"
                        render_message = upperItems[upperCurser].message
                        render_icon = upperItems[upperCurser].icon
                    elif(mainCurser == 1 and len(downerItems) > 0):
                        curMenu = "Downer"
                        render_message = downerItems[downerCurser].message
                        render_icon = downerItems[downerCurser].icon
                if keys["up"]:
                    mainCurser -= 1
                    if mainCurser < 0: mainCurser = 1
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                if keys["down"]:
                    mainCurser += 1
                    if mainCurser > 1: mainCurser = 0
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]













        



        #endregion
             
        #region 시작화면
        if game_lobby:
            listMainDowner[0].count = game_setting[2]
            listMainDowner[1].count = game_setting[2]
            listMainDowner[2].count = game_setting[3]
            listMainDowner[3].count = game_setting[3]
            game_player.update()            
        #endregion
        
        #region 게임
        if game_start and not loading: 

            #region 화면전환
            count += 1
            if(count == 10):
                print("적 출현!")
                battleManager.enemys.append(stage1.enemys[rndNum(0,2)])
            if(count == 20):
                print(battleManager.enemys[0].name)
            if(len(battleManager.player_WeaponSlot) >= game_player.behavior and not battleStart):
                if keys["enter"]: 
                    battleManager.battleStart = True
                    progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
                if keys["back"]: 
                    battleManager.player_WeaponSlot = []
                    progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
            
            if(battleManager.battleStart):
                battleManager.battle()



            #endregion           
            game_player.update()
            for enemy in battleManager.enemys:
                enemy.update()


        if(game_start and loading):
            count += 1
            game_player.update()  
            if(count == 10):
                game_player.pos = 144
                game_player.move_point = 144
                count = 0
                loading = False
        
        
        
        
        #endregion


        #region 그리기

        #region 기본
        screen.fill((0,0,0))
        menu_render.blit(menu,(-30,-30))
        submenu_x = 20
        submenu_y = 12
        #endregion
        
        #region 메인칸 텍스트
        text_color = (255, 255, 255)
        text = menuFont.render(mainUpVisual["text"],True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,90-text_rect.centery))
        text = menuFont.render(mainDownVisual["text"],True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,270-text_rect.centery))
        #endregion
        
        #region 서브칸 텍스트
        if mainCurser == 0:
            a = 0
            for i in upperItems:
                text_color = (255, 255, 255)
                text = menuFont.render(i.name,True,text_color)
                number = menuFont.render(str(i.count),True,text_color)
                b=0
                if(len(upperItems)>4):
                    b= upperCurser-2
                    if(upperCurser<3):
                        b = 0
                    if(upperCurser>len(upperItems)-3):
                        b = len(upperItems)-5
                menu_render.blit(text,(135+submenu_x,a*71+submenu_y-b*71))
                number_rect = number.get_rect()
                menu_render.blit(number,(446+submenu_x-number_rect.centerx,a*71+submenu_y-b*71))
                a += 1
        if mainCurser == 1:
            a = 0
            for i in downerItems:
                text_color = (255, 255, 255)
                text = menuFont.render(i.name,True,text_color)
                number = menuFont.render(str(i.count),True,text_color)
                b = 0
                if(len(downerItems)>4):
                    b= downerCurser-2
                    
                    if(downerCurser<3):
                        b = 0
                    if(downerCurser>len(downerItems)-3):
                        b = len(downerItems)-5
                menu_render.blit(text,(135+submenu_x,a*71+submenu_y-b*71))
                number_rect = number.get_rect()
                menu_render.blit(number,(446+submenu_x-number_rect.centerx,a*71+submenu_y-b*71))
                a += 1
        #endregion
        
        #region 선택박스 렌더링
        if(curMenu == "Main"):
            selectbox.topleft = (0,mainCurser*180)
            selectbox.width = 139
            selectbox.height = 180
        if(curMenu == "Upper"):
            a = upperCurser
            if(len(upperItems)>5):
                if(upperCurser>len(upperItems)-3):
                    a = upperCurser - len(upperItems)+5
                elif(upperCurser>2):
                    a = 2

            selectbox.topleft = (135,71*a)
            selectbox.width = 378
            selectbox.height = 75
        if(curMenu == "Downer"):
            a = downerCurser
            if(len(downerItems)>5):
                if(downerCurser>len(downerItems)-3):
                    a = downerCurser - len(downerItems)+5
                elif(downerCurser>2):
                    a = 2


            selectbox.topleft = (135,71*downerCurser)
            selectbox.width = 378
            selectbox.height = 75
        
        draw_rect_alpha(menu_render,(255,255,255,100),selectbox)      
        #endregion
        
        #region 오른쪽 메세지창,아이콘
        text_color = (255, 255, 255)
        for i in range(0,len(render_message)):            
            if(i==0): text = capitextFont.render(render_message[i],True,text_color)
            else:text = textFont.render(render_message[i],True,text_color)
            text_rect = text.get_rect()
            menu_render.blit(text,(770-text_rect.centerx,226+i*30))
        menu_render.blit(render_icon,(710,39)) 
        #endregion
        
        #region 전투중일때 그리기
        if(battleManager.battleStart):
            draw_rect_alpha(screen,(255,0,0,100),Rect(0,0,1080,720))
        #endregion

        #region 메뉴,바닥,배경 그리기 
             
        screen.blit(menu,(0,0))
        screen.blit(menu,(0,0))
        screen.blit(menu_render,(30,30))
        screen.blit(floor,(0,HEIGHT-225))

        progressBar.draw(screen)
        #endregion
        
        #region 캐릭터, 적 그리기
        game_player.draw(screen)
        for enemy in battleManager.enemys:
            enemy.draw(screen)
        #endregion
        
        #endregion

        pygame.display.flip() 



















def gameStart():
    global game_start
    global game_lobby
    global game_player
    global upperItems
    global downerItems
    global render_icon
    global render_message
    global mainCurser
    global upperCurser
    global downerCurser
    game_player.setMove(1080,10)
    game_start = True
    game_lobby = False
    mainUpVisual["text"] = "전투"
    mainUpVisual["message"] = ["전투","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"]
    mainUpVisual["icon"] = menu_icon[0]
    upperItems = game_player.weapon

    mainDownVisual["text"] = "아이템"
    mainDownVisual["message"] = ["아이템","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"]
    mainDownVisual["icon"] = menu_icon[1]   
    downerItems = game_player.item
    
    render_message = mainUpVisual["message"]
    render_icon = menu_icon[0]

    mainCurser = 0
    upperCurser = 0
    downerCurser = 0

    menuAble = True
    battleManager.player = game_player

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def setFullScreen():
    global screen
    global fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN|pygame.SCALED)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    

def rndNum(min,max):
    return random.randrange(min,max+1)






if __name__ == "__main__":
    play_game()

