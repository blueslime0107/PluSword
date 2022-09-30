
from re import A
from pip import main
import pygame
from pygame.locals import *
import time
import random

#region defaltGameSet
pygame.init()
pygame.mixer.pre_init(44100,-16,2,512)

pygame.mixer.set_num_channels(64)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

WIDTH = 1080
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH,HEIGHT))
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

clock = pygame.time.Clock()
clock_fps = 60     
TARGET_FPS = 60

fullscreen = False
#endregion
#region PictureLoad
char1 = pygame.image.load('resource\Sprites\char1.png').convert_alpha()
char2 = pygame.image.load('resource\Sprites\char2.png').convert_alpha()
menu = pygame.image.load('resource\Sprites\Menu.png').convert_alpha()
floor = pygame.image.load('resource\Sprites\Floor.png').convert_alpha()
#endregion

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

        

# class Menu:
#     def __init__(self,parentMenu,childMenu,index):
#         self.curser = 0
#         self.max_curser = index
#         try:
#             self.parentMenu = parentMenu
#             self.childMenu = childMenu
#         except:
#             pass
#     def changeCurser(self,curMenu,keypad):
#         if(keypad == "UP"):
#             self.curser -= 1
#             if(self.curser <0):
#                 self.curser = self.max_curser
#         if(keypad == "DOWN"):
#             self.curser += 1
#             if(self.curser > self.max_curser):
#                 self.curser = 0
#         if(keypad == "RIGHT"):
#             curMenu = self.childMenu
#         if(keypad == "LEFT"):
#             curMenu = self.parentMenu

stage1 = Stage(1,[Enemy("새새색",10,1),Enemy("배애앰",10,2),Enemy("장난꾸러기",10,3)])

def play_game():
    #region 기초 변수 초기화
    global screen
    global fullscreen
    playing = True
    prev_time = 0
    fullscreen = False
    count = 0

    menuAble = False
    battleBegin = False

    curStage = stage1
    curEnemys = []

    curMenu = "Main"
    mainCurser = 0
    upperCurser = 0
    downerCurser = 0

    upperItems = []
    downerItems = []

    setMenuItems(upperItems,[1,2,3])
    print()
    setMenuItems(downerItems,[4,5,6])


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
                        if event.key == pygame.K_KP6:
                            print(upperItems[upperCurser])
                        if event.key == pygame.K_KP8:
                            upperCurser -= 1
                            if upperCurser < 0: upperCurser = 1
                        if event.key == pygame.K_KP5:
                            upperCurser += 1
                            if upperCurser > 6: upperCurser = 0

                    if curMenu == "Downer":
                        if event.key == pygame.K_KP4:
                            curMenu = "Main"
                        if event.key == pygame.K_KP6:
                            print(downerItems[downerCurser])
                        if event.key == pygame.K_KP8:
                            downerCurser -= 1
                            if downerCurser < 0: downerCurser = 1
                        if event.key == pygame.K_KP5:
                            downerCurser += 1
                            if downerCurser > 6: downerCurser = 0
                    if curMenu == "Main":
                        if event.key == pygame.K_KP6:
                            if(mainCurser == 0):
                                curMenu = "Upper"
                            else:
                                curMenu = "Downer"
                        if event.key == pygame.K_KP8:
                            mainCurser -= 1
                            if mainCurser < 0: mainCurser = 1
                        if event.key == pygame.K_KP5:
                            mainCurser += 1
                            if mainCurser > 1: mainCurser = 0

                    
                    print(curMenu)















                if event.key == K_F4:
                    setFullScreen()

        
        screen.blit(menu,(0,0))
        screen.blit(floor,(0,HEIGHT-225))
        #endregion

        count += 1
        if(count == 30):
            print("Enemy Appeared!")
        if(count == 60):
            curEnemys.append(curStage.enemys[rndNum(0,2)])
            print(curEnemys[0].name)
            menuAble = True

        # if True:
        #     for ev in pygame.event.get():
        #         if ev.type == pygame.KEYDOWN: 
        #             print("1")
        #             if curMenu == 0:
        #                 print("2")
        #                 if ev.key == pygame.K_z:
        #                     print("3")

            # if curMenu == 0:
            #     if keys[pygame.K_KP5]:
            #         curCurser += 1
            #         if curCurser >= 2: 0
            #         print(curCurser)
            #     if keys[pygame.K_KP8]:
            #         curCurser -= 1
            #         if curCurser == -1: 1
            #     if keys[pygame.K_KP6]:
            #         curMenu = 1
            #         if curCurser == 0:
            #             curMenu = 1
            #         if curCurser == 1:
            #             curMenu = 2
            #         curCurser = upperCurser
            #         print(mainCurser)
                            
                    # if curMenu == 1:
                    #     if event.key == K_KP5:
                    #         curCurser += 1
                    #         if curCurser == 2: 0
                    #     if event.key == K_KP8:
                    #         curCurser -= 1
                    #         if curCurser == -1: 1
                    #     if event.key == K_KP6:
                    #         curMenu = 1
                    #         if curCurser == 0:
                    #             curMenu = 1
                    #         if curCurser == 1:
                    #             curMenu = 2
                    # if curMenu == 2:
                    #     if event.key == K_KP5:
                    #         curCurser += 1
                    #         if curCurser == 2: 0
                    #     if event.key == K_KP8:
                    #         curCurser -= 1
                    #         if curCurser == -1: 1
                    #     if event.key == K_KP6:
                    #         curMenu = 1
                    #         if curCurser == 0:
                    #             curMenu = 1
                    #         if curCurser == 1:
                    #             curMenu = 2
                              
                    # if event.key == K_KP5:
                    #     curMenu.
                    # if event.key == K_KP5 or event.key == K_KP8 or event.key == K_KP4 or event.key == K_KP6:
                   

        pygame.display.flip()

def setMenuItems(menu,item):
    a = menu
    b = item
    a = b
    return a 

def setFullScreen():
    print("active")
    global screen
    global fullscreen
    if fullscreen:
        print("fullscreen")
        screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN|pygame.SCALED)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    fullscreen = not fullscreen
    print(fullscreen)

def rndNum(min,max):
    return random.randrange(min,max+1)

if __name__ == "__main__":
    play_game()

