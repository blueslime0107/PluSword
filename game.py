
import math
import random
from select import select
import time
from re import A
from turtle import down
from cv2 import transform
from numpy import full

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
char1 = pygame.image.load('resource\Sprites\char1.png').convert_alpha()
char2 = pygame.image.load('resource\Sprites\char2.png').convert_alpha()
menu = pygame.image.load('resource\Sprites\Menu.png').convert_alpha()
floor = pygame.image.load('resource\Sprites\Floor.png').convert_alpha()
others = pygame.image.load('resource\Sprites\others.png').convert_alpha()
#endregion
a_list = []
for i in range (0,64,32):
    for j in range (0,192,32):
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(others, (0,0), Rect(j,i,32,32))
        image = pygame.transform.scale(image,(128,128))
        a_list.append(image)
menu_icon = a_list

#region FontLoad
menuFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 45)
capitextFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 30)
textFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 25)
numberFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 25)
damageFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 15)
#endregion

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
        if(self.num == 0):
            print("Manual")
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
    def __init__(self):
        self.health
        self.max_health
        self.weapon
        self.item

class Weapon:
    def __init__(self):
        self.damage
        self.level
        self.exp
        self.max_exp

class Item:
    def __init__(self):
        pass

class Enemy:
    def __init__(self, name, health, weapon):
        self.name = name
        self.health = health
        self.max_health = health
        self.weapon = weapon





stage1 = Stage(1,[Enemy("새새색",10,1),Enemy("배애앰",10,2),Enemy("장난꾸러기",10,3)])

def play_game():
    #region 기초 변수 초기화
    #region 기본변수
    global screen
    global fullscreen
    playing = True
    prev_time = 0
    fullscreen = False
    count = 0


    menuAble = False

    isLobby = True

    battleBegin = False

    curStage = stage1
    curEnemys = []

    #endregion
    # region 메인관련변수
    curMenu = "Main"
    mainCurser = 0
    upperCurser = 0
    downerCurser = 0

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

    render_message = []
    render_icon = pygame.Surface((32,32))

    selectbox = Rect(0,0,0,0)
#endregion

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

    #endregion
    while(playing):
        #region basic
        clock.tick(clock_fps)
        now = time.time()        
        dt = (now-prev_time)*TARGET_FPS        
        prev_time = now
        keys = pygame.key.get_pressed() 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 게임끄기
                playing = False
            if event.type == pygame.KEYDOWN: 
                if(menuAble):
                    if curMenu == "Upper":
                        if event.key == pygame.K_KP4:
                            curMenu = "Main"
                            render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                            render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                        if event.key == pygame.K_KP6:
                            upperItems[upperCurser].active() # 아이템 발동
                        if event.key == pygame.K_KP8:
                            upperCurser -= 1
                            if upperCurser < 0: upperCurser = len(upperItems)-1
                            render_message = upperItems[upperCurser].message
                            render_icon = upperItems[upperCurser].icon
                        if event.key == pygame.K_KP5:
                            upperCurser += 1
                            if upperCurser >= len(upperItems): upperCurser = 0
                            render_message = upperItems[upperCurser].message
                            render_icon = upperItems[upperCurser].icon
                    if curMenu == "Downer":
                        if event.key == pygame.K_KP4:
                            curMenu = "Main"
                            render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                            render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                        if event.key == pygame.K_KP6:
                            downerItems[downerCurser].active() # 아이템 발동
                            
                        if event.key == pygame.K_KP8:
                            downerCurser -= 1
                            if downerCurser < 0: downerCurser = len(downerItems)-1
                            render_message = downerItems[downerCurser].message
                            render_icon = downerItems[downerCurser].icon
                        if event.key == pygame.K_KP5:
                            downerCurser += 1
                            if downerCurser >= len(downerItems): downerCurser = 0
                            render_message = downerItems[downerCurser].message
                            render_icon = downerItems[downerCurser].icon
                    if curMenu == "Main":
                        if event.key == pygame.K_KP6:
                            if(mainCurser == 0):
                                curMenu = "Upper"
                                render_message = upperItems[upperCurser].message
                                render_icon = upperItems[upperCurser].icon
                            else:
                                curMenu = "Downer"
                                render_message = downerItems[downerCurser].message
                                render_icon = downerItems[downerCurser].icon
                        if event.key == pygame.K_KP8:
                            mainCurser -= 1
                            if mainCurser < 0: mainCurser = 1
                            render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                            render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                        if event.key == pygame.K_KP5:
                            mainCurser += 1
                            if mainCurser > 1: mainCurser = 0
                            render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                            render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]











                if event.key == K_F4:
                    setFullScreen()

        



        #endregion
        #region 게임진행 메인
        count += 1

        if isLobby:
            listMainDowner[0].count = game_setting[2]
            listMainDowner[1].count = game_setting[2]
            listMainDowner[2].count = game_setting[3]
            listMainDowner[3].count = game_setting[3]
            
        # if(count == 30):
        #     print("Enemy Appeared!")
        # if(count == 60):
        #     curEnemys.append(curStage.enemys[rndNum(0,2)])
        #     print(curEnemys[0].name)
        menuAble = True
        #endregion
        #region 그리기
        menu_render.blit(menu,(-30,-30))
        submenu_x = 20
        submenu_y = 12
        #region mainText
        text_color = (255, 255, 255)
        text = menuFont.render(mainUpVisual["text"],True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,90-text_rect.centery))
        text = menuFont.render(mainDownVisual["text"],True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,270-text_rect.centery))
        #endregion
        #region subText
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
        #region setSelectBoxRect
        if(curMenu == "Main"):
            selectbox.topleft = (0,mainCurser*180)
            selectbox.width = 139
            selectbox.height = 180
        if(curMenu == "Upper"):
            a = upperCurser
            if(upperCurser>len(upperItems)-3):
                a = upperCurser - len(upperItems)+5
            elif(upperCurser>2):
                a = 2

            selectbox.topleft = (135,71*a)
            selectbox.width = 378
            selectbox.height = 75
        if(curMenu == "Downer"):
            a = downerCurser
            if(downerCurser>len(downerItems)-3):
                a = downerCurser - len(downerItems)+5
            elif(downerCurser>2):
                a = 2


            selectbox.topleft = (135,71*downerCurser)
            selectbox.width = 378
            selectbox.height = 75
        
        draw_rect_alpha(menu_render,(255,255,255,100),selectbox)      
        #endregion
        


        # if(curMenu == "Main"):
        text_color = (255, 255, 255)
        for i in range(0,len(render_message)):            
            if(i==0): text = capitextFont.render(render_message[i],True,text_color)
            else:text = textFont.render(render_message[i],True,text_color)
            text_rect = text.get_rect()
            menu_render.blit(text,(770-text_rect.centerx,226+i*30))

        menu_render.blit(render_icon,(710,39))





        screen.blit(menu,(0,0))
        screen.blit(menu_render,(30,30))
        screen.blit(floor,(0,HEIGHT-225))
        #endregion
        pygame.display.flip() 


























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

