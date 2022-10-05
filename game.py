
from glob import glob
from json import load
import math
from os import curdir
from pickle import FALSE
import random
from select import select
import time
from re import A
from turtle import down
from cv2 import transform
from numpy import block, full, number, save
from copy import copy

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
battleMenu_render = pygame.Surface((1080,416), SRCALPHA)
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
battleMenu = pygame.image.load('resource\Sprites\BattleMenu.png').convert_alpha()
stage1Bg = [pygame.image.load('resource\Sprites\stage1\\bga.png').convert_alpha(),
pygame.image.load('resource\Sprites\stage1\\bgb1.png').convert_alpha(),
pygame.image.load('resource\Sprites\stage1\\bgb2.png').convert_alpha(),
pygame.image.load('resource\Sprites\stage1\\bgb3.png').convert_alpha(),
pygame.image.load('resource\Sprites\stage1\land.png').convert_alpha()]
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
a_list = []
for i in range (0,256,128):
    for j in range (0,384,96):
        image = pygame.Surface((96, 128), pygame.SRCALPHA)
        image.blit(char1, (0,0), Rect(j,i,96,128))
        a_list.append(image)
spr_char1 = a_list

#endregion
#region FontLoad
menuFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 45)
capitextFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 30)
textFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 25)

weaponFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 40)
numberFont = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 50)
damageFont = pygame.font.Font("resource\Font\SEBANG Gothic.ttf", 15)
#endregion
#region settingLoad
try:
    setting = open("setting.txt", 'r', encoding="UTF-8")
except: 
    with open("setting.txt",'w',encoding="UTF-8") as f:
        f.write(str(game_setting[2])+"\n")
        f.write(str(game_setting[3])+"\n")   
    setting = open("setting.txt", 'r', encoding="UTF-8")
lines = setting.readlines()
setting_scroll = []
for line in lines:
    line = line.strip()
    setting_scroll.append(line)
game_setting[2] = int(setting_scroll[0])
game_setting[3] = int(setting_scroll[1])
with open("setting.txt",'w',encoding="UTF-8") as f:
    f.write(str(game_setting[2])+"\n")
    f.write(str(game_setting[3])+"\n")
#endregion
#region
cur_list = []
for i in range(1,256):
    radius = 6
    image = pygame.Surface((radius*i,radius*i), pygame.SRCALPHA)   
    pygame.draw.circle(image, (255,255,255,256-i), image.get_rect().center, radius*i//2,10)
    cur_list.append(image)
white_circle = cur_list
cur_list = []
for i in range(1,255,4):
    width = 256-i
    image = pygame.Surface((width,width), pygame.SRCALPHA)
    rect2 = round(image.get_width()/2)
    pygame.draw.circle(image, (255,255,255,256-i), (rect2,rect2), 1 if rect2-1 < 1 else rect2-1,1)
    cur_list.append(image)
died_white_circle = cur_list

enemyAppearSprite = pygame.Surface((WIDTH,200), SRCALPHA)
enemyAppearSprite.fill((0,0,0,180))
text = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 180).render("적 출현!",True,(255,255,255))
text_rect = text.get_rect()
enemyAppearSprite.blit(text,(540-text_rect.centerx,10))
bossAppearSprite = pygame.Surface((WIDTH,200), SRCALPHA)
bossAppearSprite.fill((0,0,0,180))
text = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 180).render("보스 출현!",True,(255,255,255))
text_rect = text.get_rect()
bossAppearSprite.blit(text,(540-text_rect.centerx,10))
ItemAppearSprite = pygame.Surface((WIDTH,120), SRCALPHA)
ItemAppearSprite.fill((0,0,0,180))
text = pygame.font.Font("resource\Font\SEBANG Gothic Bold.ttf", 100).render("아이템 선택!",True,(255,255,255))
text_rect = text.get_rect()
ItemAppearSprite.blit(text,(540-text_rect.centerx,10))
#endregion
def updateSetting(a,b):
    with open("setting.txt",'w',encoding="UTF-8") as f:
        f.write(str(a)+"\n")
        f.write(str(b)+"\n")    

def convertImage(surface,x,y,w,h,multi=5):
    image = pygame.Surface((w, h), pygame.SRCALPHA)
    image.blit(surface, (0,0), Rect(x,y,w,h))
    image = pygame.transform.scale(image,(w*multi,h*multi))
    return image

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
    
def bigLeftChange(a,b):
    var1 = a
    var2 = b
    if var2 > var1:
        aaa = var2
        var2 = var1
        var1 = aaa
    return var1, var2

def rndNum(min,max):
    return random.randrange(min,max+1)
def rndTup(value):
    return random.randrange(value[0],value[1]+1)

def mixList(origin_list):
    origin = copy(origin_list)
    rand_list = []
    for i in range(0,len(origin)):
        rnd = rndNum(0,len(origin)-1)
        rand_list.append(origin[rnd])
        del origin[rnd]
    return rand_list

def className(object,string):
    return object.__class__.__name__ == string

class LobbyItem:
    def __init__(self,name, message=[""], icon=pygame.Surface((16,16))):
        self.text = name
        self.message = message
        self.icon = icon   

class MainItem:
    def __init__(self,num, name, message=[""], icon=pygame.Surface((16,16))):
        self.num = num
        self.name = name
        self.count = 0
        self.message = message
        self.icon = icon
    def active(self):
        global gameReset
        global game_setting
        global fullscreen
        global game_player
        global game_start
        global game_lobby, gameReset
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
            updateSetting(game_setting[2],game_setting[3])
        if(self.num == 6):
            game_setting[2] -= 5
            if(game_setting[2]<0): game_setting[2] = 0
            self.count = game_setting[2]
            updateSetting(game_setting[2],game_setting[3])
        if(self.num == 7):
            game_setting[3] += 5
            if(game_setting[3]>100): game_setting[3] = 100
            self.count = game_setting[3]
            updateSetting(game_setting[2],game_setting[3])
        if(self.num == 8):
            game_setting[3] -= 5
            if(game_setting[3]<0): game_setting[3] = 0
            self.count = game_setting[3]
            updateSetting(game_setting[2],game_setting[3])
        if(self.num == 9):          
            setFullScreen()
            self.count = int(fullscreen)

        if(self.num == 10):
            gameReset = True
            







class Num:
    def __init__(self, value=0):
        self.value =value
        self.text = str(value)
class Sim:
    def __init__(self, value="+"):
        self.value = value
        self.text = str(value)

class Weapon:
    def __init__(self,name,id,icon=pygame.Surface((16,16)),level=0,lvUpList = [2,4,8,16,32], message=[""]):
        self.tag = "Weapon"
        self.id = id 
        self.count = level
        
        self.exp = 0
        self.max_exp = 0
        self.lvUpList = lvUpList
        self.lvUpList.append(999)
        self.time = 300
        self.max_time = self.time

        self.name = name        
        self.message = message
        self.icon = icon

        self.rndList = []
        self.rndList2 = []
        self.dmgList = []

        self.damage = 0
        self.add_damage = 0

        self.preSetWeapon()


    def active(self):
        global battleManager
        if(len(battleManager.player_WeaponSlot) < game_player.behavior):
            battleManager.addPlayerWeaponSlot(self)
            progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
    def preSetWeapon(self):
        if self.id == 1:
            self.rndList = [(1,9),(10,20),(30,70),(50,100),(100,500),(500,1000)]
            self.rndList2 = [(1,9),(1,9),(10,20),(30,60),(50,100),(200,600)]
            self.dmgList = [1,2,4,8,16,32]
        elif self.id == 2:
            self.rndList = [(1,9),(10,20),(30,70),(50,100),(100,500),(500,1000)]
            self.rndList2 = [(1,9),(1,9),(10,20),(30,60),(50,100),(200,600)]
            self.dmgList = [1,2,4,8,16,32]
        elif self.id == 6:
            self.rndList = [(1,3),(2,9),(11,14),(11,16),(17,23),(50,100)]
            self.rndList2 = [(1,3),(2,9),(2,5),(11,16),(13,20),(30,80)]
            self.dmgList = [1,2,4,8,16,32]
        elif self.id == 7:
            self.rndList = [(1,3),(2,9),(11,14),(11,16),(17,23),(50,100)]
            self.rndList2 = [(1,3),(2,9),(2,5),(11,16),(13,20),(30,80)]
            self.dmgList = [1,2,4,8,16,32]
        else:
            self.rndList = [(1,9),(10,20),(30,70),(50,100),(100,500),(500,1000)]
            self.dmgList = [1,2,4,8,16,32] 
        self.damage = self.dmgList[self.count]   
        self.max_exp = self.lvUpList[self.count]   
    def getWeapon(self):
        question = []
        answer = []
        if self.id == 1:
            a = rndTup(self.rndList[self.count])
            b = rndTup(self.rndList2[self.count])
            c = a + b
            question = [Num(a),Sim("+"),Num(b),Sim("="),Num(c)]
            answer = [4]
        if self.id == 2:
            a = rndTup(self.rndList[self.count])
            b = rndTup(self.rndList2[self.count])
            a,b = bigLeftChange(a,b)
            c = a - b
            question = [Num(a),Sim("-"),Num(b),Sim("="),Num(c)]
            answer = [4]
        if self.id == 3:
            a = rndNum(1,9)
            b = rndNum(1,9)
            rnd = rndNum(0,1)
            sim = ""
            if(rnd == 0):
                c = a + b
                sim = "+"
            else:
                a,b= bigLeftChange(a,b)
                c = a - b
                sim = "-"  
            question = [Num(a),Sim(sim),Num(b),Sim("="),Num(c)]
            answer = [4]
        if self.id == 4:
            randa = rndNum(3,6)
            b = 0
            question = []
            for i in range(0,randa):
                rnd = rndNum(1,5)
                question.append(Num(rnd))
                question.append(Sim("+"))
                b += rnd
            del question[len(question)-1]

            question.append(Sim("="))
            question.append(Num(b))

            answer = [len(question)-1]
        if self.id == 5:
            a = rndNum(1,9)
            b = rndNum(1,9)
            rnd = rndNum(0,1)
            sim = ""
            if(rnd == 0):
                c = a + b
                sim = "+"
            else:
                a,b=bigLeftChange(a,b)
                c = a - b
                sim = "-"  
            question = [Num(a),Sim(sim),Num(b),Sim("="),Num(c)]
            answer = [rndNum(0,1)*2]
        if self.id == 6:
            a = rndTup(self.rndList[self.count])
            b = rndTup(self.rndList2[self.count]) 
            c = a * b
            question = [Num(a),Sim("×"),Num(b),Sim("="),Num(c)]  
            answer = [4]   
        if self.id == 7:
            a = rndTup(self.rndList[self.count])
            b = rndTup(self.rndList2[self.count]) 
            c = a * b
            question = [Num(c),Sim("÷"),Num(b),Sim("="),Num(a)]  
            answer = [4]  
        
        
        return question, answer 
        
          













    def levelRndNum(self):
        rndNum(1,9)

    def levelUp(self):
        self.exp = 0
        self.count += 1
        if self.count >= 5:
            self.max_exp = 0
            self.count = 5
        else:
            self.max_exp = self.lvUpList[self.count]
        self.damage = self.dmgList[self.count]
        

class Item:
    def __init__(self,name,id,level=0, message=[""], icon=pygame.Surface((16,16))):
        self.tag = "Weapon"
        self.id = id 
        self.count = level
        self.time = 300
        self.max_time = self.time

        self.name = name        
        self.message = message
        self.icon = icon
        self.equip = False
    def active(self):
        if(self.id == 1):
            battleManager.player.heal(5)
            self.kill()
        if(self.id == 2):
            battleManager.player.max_health += 10
            battleManager.player.health += 10
            self.kill()
        if(self.id == 3):
            self.equip = True
    def equip_active(self,weapon):
        if self.id == 3:
            weapon.levelUp()
        self.kill()

    def kill(self):
        global downerCurser, downerItems
        battleManager.player.item.remove(self)
        if downerCurser == len(downerItems) : downerCurser -=1

class Player:
    def __init__(self,name="삼각",sprite=spr_mainChar1[0],health=10):
        self.tag = "Player"
        self.pos = 144
        self.saved_pos = self.pos
        self.name = name

        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        self.sprite = sprite
        self.health = health
        self.max_health = self.health
        self.weapon = []
        self.item = []
        self.behavior = 3
        self.time_beul = 3

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
        
        self.name_surface = capitextFont.render(self.name,True,(255,255,255))        
        self.name_surface_rect = self.name_surface.get_rect()
        draw_rect_alpha(self.name_surface,(0,0,0,200),self.name_surface_rect)
        self.name_surface.blit(capitextFont.render(self.name,True,(255,255,255)),(0,0))
        self.health_surface = pygame.Surface((180, 15))
        self.health_surface_rect = self.health_surface.get_rect()

        self.death = False

    def update(self):
        if self.death: return
        if(self.pos != self.move_point):
            self.moving = True
            dx = self.move_point - self.pos
            dx /= self.move_speed
            self.pos += dx
            if(abs(self.move_point-self.pos)<2):
                self.moving = False
                self.pos = self.move_point

    def draw(self,screen):
        if self.death: return
        if(self.condition == 0 or self.condition == 1):
            self.count += 1
            if(self.count % self.idlespd == 0):
                if(self.condition == 0):
                    self.condition = 1
                    self.count = 0
                    self.image = self.idle1
                elif(self.condition == 1):
                    self.condition = 0
                    self.count = 0
                    self.image = self.idle2
        if(self.condition == 2):
            self.image = self.ready
        if(self.condition == 3):
            self.image = self.attack

        if(self.condition == 4):
            self.image = self.damage

        screen.blit(self.image,(self.pos-self.image.get_rect().centerx,CHARY))
        screen.blit(self.name_surface,(self.pos-self.name_surface_rect.centerx,CHARY-25))

        self.health_surface.fill((0,0,0))
        pygame.draw.rect(self.health_surface, (255,255,255), (3,3,self.health/self.max_health*174,9))
        screen.blit(self.health_surface,(self.pos-self.health_surface_rect.centerx,CHARY+160))
        health_text = capitextFont.render(str(self.health),True,(0,0,0))
        health_text.fill((0,0,0))
        health_text.blit(capitextFont.render(str(self.health),True,(255,255,255)),(0,0))
        screen.blit(health_text,(self.pos-health_text.get_rect().centerx,CHARY+160+15))


    def setMove(self,pos,spd):
        self.move_point = pos
        self.move_speed = spd

    def giveWeapon(self,weapon):
        self.weapon.append(copy(weapon))
    def giveItem(self,item):
        self.item.append(copy(item))
    def heal(self,value):
        self.health += value
        if self.health > self.max_health: self.health = self.max_health

class Enemy:
    def __init__(self,name,sprite,health,weapon = Weapon("",0,0),spd = 1):
        self.tag = "Enemy"
        self.pos = 1100
        self.saved_pos = 0
        self.name = name

        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        self.sprite = sprite
        self.health = health
        self.max_health = self.health
        self.weapon = copy(weapon)
        self.speed = spd
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

        self.name_surface = capitextFont.render(self.name,True,(255,255,255))   
        self.name_surface_rect = self.name_surface.get_rect()
        draw_rect_alpha(self.name_surface,(0,0,0,200),self.name_surface_rect)
        self.name_surface.blit(capitextFont.render(self.name,True,(255,255,255)),(0,0))
        self.health_surface = pygame.Surface((180, 15))
        self.health_surface_rect = self.health_surface.get_rect()
    def draw(self,screen):
        if(self.condition == 0 or self.condition == 1):
            self.count += 1
            if(self.count % self.idlespd == 0):
                if(self.condition == 0):
                    self.condition = 1
                    self.count = 0
                    self.image = self.idle1
                elif(self.condition == 1):
                    self.condition = 0
                    self.count = 0
                    self.image = self.idle2
        if(self.condition == 2):
            self.image = self.ready
        if(self.condition == 3):
            self.image = self.attack

        if(self.condition == 4):
            self.image = self.damage

        screen.blit(pygame.transform.flip(self.image,True,False),(self.pos-self.image.get_rect().centerx,CHARY))
        screen.blit(self.name_surface,(self.pos-self.name_surface_rect.centerx,CHARY-25))

        self.health_surface.fill((0,0,0))
        pygame.draw.rect(self.health_surface, (255,255,255), (3,3,self.health/self.max_health*174,9))
        screen.blit(self.health_surface,(self.pos-self.health_surface_rect.centerx,CHARY+160))
        health_text = capitextFont.render(str(self.health),True,(0,0,0))
        health_text.fill((0,0,0))
        health_text.blit(capitextFont.render(str(self.health),True,(255,255,255)),(0,0))
        screen.blit(health_text,(self.pos-health_text.get_rect().centerx,CHARY+160+15))

    def update(self):
        if(self.pos != self.move_point):
            self.moving = True
            dx = self.move_point - self.pos
            dx /= self.move_speed
            self.pos += dx
            if(abs(self.move_point-self.pos)<2):
                self.moving = False
                self.pos = self.move_point
                if(self.saved_pos == 0): self.saved_pos = self.pos

    def setMove(self,pos,spd):
        self.move_point = pos
        self.move_speed = spd

    def changeSavePos(self,pos):
        self.pos = pos
        self.move_point = pos
        self.saved_pos = pos

    def setlevel(self,level,spd,health):
        self.count = level
        self.speed += spd
        self.max_health *= health
        self.health = self.max_health

class Stage:
    def __init__(self,num,enemys = []):
        self.index = -1
        self.num = num
        self.enemys = enemys
        self.enemy_line = []
        try:self.preSetStage()
        except:pass
    def preSetStage(self):
        global game_player
        if battleManager.player.name == "삼각":
            self.enemy_line = [
                [copy(self.enemys[0])],[copy(self.enemys[1])],[copy(self.enemys[2])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[copy(self.enemys[3])],\
                    [copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])]\
                        ,[copy(self.enemys[rndNum(0,1)]),copy(self.enemys[rndNum(0,1)]),copy(self.enemys[2])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[self.enemys[4]]
            ]
            
        if battleManager.player.name == "지사":
            self.enemy_line = [
                [copy(self.enemys[0])],[copy(self.enemys[1])],[copy(self.enemys[2])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[self.enemys[4]],\
                    [copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])]\
                        ,[copy(self.enemys[rndNum(0,1)]),copy(self.enemys[rndNum(0,1)]),copy(self.enemys[2])],[copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)]),copy(self.enemys[rndNum(0,2)])],[copy(self.enemys[3])]
            ]
        self.enemy_line[3][0].setlevel(1,0,2)
        self.enemy_line[3][1].setlevel(1,0,2)
        self.enemy_line[4][0].setlevel(2,0,1)
        self.enemy_line[5][0].setlevel(2,1,2)
        self.enemy_line[5][1].setlevel(2,1,2)
        self.enemy_line[6][0].setlevel(3,1,2)
        self.enemy_line[6][1].setlevel(3,1,3)
        self.enemy_line[7][0].setlevel(1,2,3)
        self.enemy_line[7][1].setlevel(3,2,2)
        self.enemy_line[7][2].setlevel(2,2,3)
        self.enemy_line[8][0].setlevel(3,2,4)
        self.enemy_line[8][1].setlevel(4,2,3)
        self.enemy_line[8][2].setlevel(2,2,2)
        self.enemy_line[9][0].setlevel(5,3,5)
    def getEnemy(self):
        self.index += 1
        return self.enemy_line[self.index]

class BattleManager:
    def __init__(self):
        self.player = Player()
        self.enemys = []

        self.player_WeaponSlot = []

        self.battle_Chain = []
        self.battle_Chain_max = 0

        self.battleStart = False
        self.battlePre = False
        self.count = 0

        self.stage1 = Stage(1,[enemys["새새색"],enemys["배애앰"],enemys["장난질"],enemys["직각"],enemys["마르"]])
        # self.stage2 = Stage(2,[enemys["새새색"],enemys["배애앰"],enemys["장난질"]])
        # self.stage3 = Stage(3,[enemys["새새색"],enemys["배애앰"],enemys["장난질"]])
        self.curStage = self.stage1

        self.item_get = False
        self.randItems = []
        self.itemEquip = False

    def addPlayerWeaponSlot(self,weapon):
        self.player_WeaponSlot.append(Battle(self.player,weapon))

    def battle(self):
        if not self.battlePre:
            enemy_WeaponSlot = []
            for enemy in self.enemys:
                for _ in range(0,enemy.speed):
                    enemy_WeaponSlot.append(Battle(enemy,enemy.weapon))

            self.battle_Chain.extend(self.player_WeaponSlot)
            self.battle_Chain.extend(enemy_WeaponSlot)

            self.battle_Chain = mixList(self.battle_Chain)
            

            self.battle_Chain_max = len(self.battle_Chain)
            progressBar.updateProgress(self.battle_Chain,self.battle_Chain_max)
            self.battlePre = True

        if(len(self.battle_Chain) > 0):
            self.match()

        else:
            self.battleStart = False

    def match(self):
        self.count += 1
        self.battle_Chain[0].update(game_player,self.enemys)
        progressBar.updateProgress(self.battle_Chain,self.battle_Chain_max)

    def setEnemys(self):
        for index in self.curStage.getEnemy():
            self.enemys.append(copy(index))

    def suffleItem(self):
        self.randItems = []
        self.randItems.append(copy(items["포도당"]))
        self.randItems.append(copy(items["정신극복"]))
        self.randItems.append(copy(items["숫돌"]))
        self.randItems.append(copy(weapons["마너스검"]))
        self.randItems.append(copy(weapons["구구단검"]))


      

class Battle:
    def __init__(self,attack,weapon):
        self.attack = attack
        self.defend = 0
        self.weapon = copy(weapon)
        self.originWeapon = weapon
        self.first = True
        self.question = []
        self.answer = []
        self.input = ""
        self.failed = False

        self.delay = False
        self.bool = False
        self.bool2 = False
        self.count = 0
    def update(self,player,enemys):
        global keys, stamp_list, screenCount
        #region 전투돌입 전
        if(self.first):       
            if(len(self.question) == 0): self.question, self.answer = self.weapon.getWeapon()  
              
            if(self.attack.tag == "Player"):
                self.defend = enemys[0]
                self.attack.setMove(540-CENTERDIS,10)
                self.defend.setMove(540+CENTERDIS,10)
            if(self.attack.tag == "Enemy"):
                self.defend = player
                self.attack.setMove(540+CENTERDIS,10)
                self.defend.setMove(540-CENTERDIS,10)

            
            self.attack.condition = 2
            self.defend.condition = 2 
            self.first = False
        player = self.attack if self.attack.tag == "Player" else self.defend
        enemy = self.attack if self.attack.tag == "Enemy" else self.defend
        #endregion

        #region 전투돌입
        knockback = 100
        if(self.input != "" and not self.delay and not self.failed): # 답 입력시
            if(len(str(self.question[self.answer[0]].value)) == len(self.input)):
                if(self.question[self.answer[0]].value == int(self.input)):
                    self.originWeapon.exp += 1
                    if self.originWeapon.exp >= self.originWeapon.max_exp: 
                        self.originWeapon.levelUp()
                    
                    if(self.attack.tag == "Player"):
                        self.attack.condition = 3
                        self.defend.condition = 4
                        if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul:
                            self.weapon.damage *= 2
                        self.defend.health -=  self.weapon.damage+self.weapon.add_damage
                        self.attack.setMove(540-CENTERDIS-knockback,10)
                        self.defend.setMove(540+CENTERDIS+knockback,10)
                    if(self.defend.tag == "Player"):
                        self.attack.condition = 3
                        self.defend.condition = 3
                        if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul:
                            self.attack.health -=  math.ceil((self.weapon.damage+self.weapon.add_damage)/2)
                        self.attack.condition = 4
                        self.attack.setMove(540+CENTERDIS+knockback//2,10)
                        self.defend.setMove(540-CENTERDIS-knockback//2,10)
                    self.weapon.time = 0
                    self.bool = True
                    self.delay = True
                else:
                    self.input = ""
                    self.failed = True
                    self.weapon.time = 0

        if self.delay:
            self.count += 1
            # if self.input == "" and not self.bool: self.count += 30
            if self.count > 30: 
                self.count = 0
                self.delay = False
                
                if self.bool2: self.bool = True
                if not self.bool2:
                    enemy = self.attack if self.attack.tag == "Enemy" else self.defend
                    if enemy.health <= 0:
                        x = 80
                        y = 80
                        stamp_list.append(Stamp((enemy.pos+120+x,CHARY+y),1))
                        stamp_list.append(Stamp((enemy.pos-120+x,CHARY+y),1))
                        stamp_list.append(Stamp((enemy.pos+x,CHARY+120+y),1))
                        stamp_list.append(Stamp((enemy.pos+x,CHARY-120+y),1))
                        screenCount += 20
                        del battleManager.enemys[0]
                        for battle in battleManager.battle_Chain[:]:
                            if(battle.attack == self.defend):
                                battleManager.battle_Chain.remove(battle)
                        if(len(battleManager.enemys) <= 0):
                            battleManager.battle_Chain = []
                else:
                    player = self.attack if self.attack.tag == "Player" else self.defend
                    if player.health <= 0:
                        x = -80
                        y = 80
                        stamp_list.append(Stamp((player.pos+120+x,CHARY+y),1))
                        stamp_list.append(Stamp((player.pos-120+x,CHARY+y),1))
                        stamp_list.append(Stamp((player.pos+x,CHARY+120+y),1))
                        stamp_list.append(Stamp((player.pos+x,CHARY-120+y),1))
                        screenCount += 20
                        player.death = True
                        battleManager.battle_Chain = []
                    
                        
        else:
            self.inputNum()
            self.weapon.time -= 1
        #endregion
                

        #region 전투끝
        if(self.weapon.time <= 0 and not self.delay):   

            if not self.bool:
                if self.originWeapon.count != 5:
                    self.originWeapon.exp += 1
                    if self.originWeapon.exp >= self.originWeapon.max_exp: 
                        self.originWeapon.levelUp()
                    
                if(self.attack.tag == "Enemy"):
                    self.attack.condition = 3
                    self.defend.condition = 4
                    self.defend.health -=  self.weapon.damage +self.weapon.add_damage
                    self.attack.setMove(540+CENTERDIS+knockback//2,10)
                    self.defend.setMove(540-CENTERDIS-knockback//2,10)

                if(self.defend.tag == "Enemy"):
                    self.attack.condition = 4
                    self.defend.condition = 3
                    # if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul:
                    #     self.weapon.damage *= 2
                    self.attack.health -=  math.ceil((self.weapon.damage+self.weapon.add_damage)/2)
                    self.attack.setMove(540-CENTERDIS-knockback,10)
                    self.defend.setMove(540+CENTERDIS+knockback,10)


                self.delay = True
                self.bool2 = True

            if self.bool:
                try:
                    if(len(battleManager.battle_Chain) >= 1):       
                        del battleManager.battle_Chain[0]
                        if(not battleManager.battle_Chain[0].attack == enemy or not battleManager.battle_Chain[0].defend == enemy):
                            enemy.image = enemy.idle1
                            enemy.condition = 0
                            enemy.setMove(enemy.saved_pos,5)
                except:pass
            if len(battleManager.battle_Chain) <= 0:
                self.battleEnd()
        #endregion

    def draw(self,board):
        if(len(self.question) == 0): self.question, self.answer = self.weapon.getWeapon()
        ganguk = 5
        
        text_color = (255,255,255)
        text_name = weaponFont.render(self.weapon.name,True,text_color)
        text_level = weaponFont.render("Lv " + str(self.weapon.count),True,text_color)
        text_time = weaponFont.render(str(math.ceil(self.weapon.time / 60)),True,text_color)
        text_input = numberFont.render(self.input,True,(0,0,0))

        size = 0
        for text in range(0,len(self.question)):            
            text_num = numberFont.render(self.question[text].text,True,text_color)           
            size += text_num.get_rect().width + ganguk
        question_render = pygame.Surface((size,213), SRCALPHA)
        x = 0
        for text in range(0,len(self.question)):            
            text_num = numberFont.render(self.question[text].text,True,text_color)         
            if(text in self.answer): 
                text_num.fill((255,255,255))  
                text_num.blit(text_input,(0,0))

            question_render.blit(text_num,(x,0))
            x += text_num.get_rect().width + ganguk
        board.blit(question_render,(207+410-size//2,112+86))

        board.blit(self.weapon.icon,(16,16))
        board.blit(text_name,(263+40,27))
        board.blit(text_level,(151+40,27))
        board.blit(text_time,(41,351))
        pygame.draw.rect(board, (0,255,255) if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul else (255,255,255) , Rect(116,352,self.weapon.time/self.weapon.max_time*946,50), width=0)     



    def moveBack(self):
        battleManager.player.setMove(battleManager.player.saved_pos,5)
        for enemy in battleManager.enemys:
            enemy.setMove(enemy.saved_pos,5)

    def battleEnd(self):
        global curMenu, mainCurser
        battleManager.player.image = battleManager.player.idle1
        battleManager.player.condition = 0
        for enemy in battleManager.enemys:
            enemy.image = enemy.idle1
            enemy.condition = 0
        battleManager.battleStart = False
        self.moveBack()
        battleManager.player_WeaponSlot = []
        battleManager.battlePre = False
        curMenu = "Main"
        mainCurser = 0

    def inputNum(self):
        if keys["0"]: self.input += "0"
        if keys["1"]: self.input += "1"
        if keys["2"]: self.input += "2"
        if keys["3"]: self.input += "3"
        if keys["4"]: self.input += "4"
        if keys["5"]: self.input += "5"
        if keys["6"]: self.input += "6"
        if keys["7"]: self.input += "7"
        if keys["8"]: self.input += "8"
        if keys["9"]: self.input += "9"
        if keys["back"]: self.input = ""
        if keys["minus"]: self.input += "-"

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
            color = (0,0,0)
            if index.attack.tag == "Player":
                color = (0,255,0)
            if index.attack.tag == "Enemy":
                color = (0,255,255)
            self.render_final.append(ProgressBox(0,0,color))
        self.render_max = max

    def draw(self,screen):
        self.render = progress.copy()
        blocksize = 1044
        blocksize /= self.render_max
        for index in range(0,len(self.render_list)):
            self.render_final[index].draw(self.render,index,blocksize)
        screen.blit(self.render,(0,410))

class BackGround:
    def __init__(self,image,speed,y):
        self.image = pygame.transform.scale2x(image)
        self.speed = speed
        self.y = y
        self.x = self.image.get_rect().width
    def draw(self,bgx):
        rel_x = -bgx*self.speed % self.x 
        screen.blit(self.image, (rel_x - self.x ,self.y))
        if rel_x < self.x :
            screen.blit(self.image,(rel_x,self.y))
        bgx += 1 

class Stamp:
    def __init__(self, pos, num):
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA) # 이미지          
        self.rect = self.image.get_rect()
        self.image2 = self.image.copy()
        self.pos = pos
        self.count = 0
        self.count2 = 0
        self.count3 = 0
        self.num = num

    def update(self):
        global stamp_list
        if self.num == 1: # 커지는 투명 원
            self.count += 2
            try:self.image = white_circle[self.count]
            except: stamp_list.remove(self)
        if self.num == 2 or self.num == 3 or self.num == 4:
            self.count += 40
            if self.count >= 540:
                self.count = 540
                self.count2 += 20

                if self.count2 >= 540:
                    self.count3 += 60
                    if self.count3 >= 540:
                        stamp_list.remove(self)

    def draw(self,screen):
        if self.num == 1: screen.blit(self.image,self.image.get_rect(center = self.pos))
        if self.num == 2:
            screen.blit(enemyAppearSprite,(-540+self.count,200-self.count3),(0,0,540,200))
            screen.blit(enemyAppearSprite,(1080-self.count,200-self.count3),(540,0,540,200))
        if self.num == 3:
            screen.blit(bossAppearSprite,(-540+self.count,200-self.count3),(0,0,540,200))
            screen.blit(bossAppearSprite,(1080-self.count,200-self.count3),(540,0,540,200))
        if self.num == 4:
            screen.blit(ItemAppearSprite,(-540+self.count,150-self.count3),(0,0,540,200))
            screen.blit(ItemAppearSprite,(1080-self.count,150-self.count3),(540,0,540,200))









CHARY = 474
CENTERDIS = 50

keys = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "enter": False,
    "back": False,
    "0": False,
    "1": False,
    "2": False,
    "3": False,
    "4": False,
    "5": False,
    "6": False,
    "7": False,
    "8": False,
    "9": False,
    "minus": False

}

weapons = { 
    "플러스검": Weapon("플러스검",1, convertImage(spr_mainChar1[0],64,0,32,32,4)),
    "마너스검": Weapon("마너스검",2, convertImage(spr_mainChar1[1],64,0,32,32,4)),
    "쪼기": Weapon("쪼기",3,convertImage(spr_char1[0],64,0,32,32,4)),
    "뱀꼬리": Weapon("뱀꼬리",4,convertImage(spr_char1[1],64,0,32,32,4)),
    "부메랑": Weapon("부메랑",5,convertImage(spr_char1[2],64,0,32,32,4)),
    "구구단검": Weapon("구구단검",6,convertImage(spr_mainChar1[2],64,0,32,32,4)),
    "나누창": Weapon("나누창",7,convertImage(spr_mainChar1[3],64,0,32,32,4))
}

items = {
    "포도당": Item("포도당",1),
    "정신극복": Item("정신극복",2),
    "숫돌": Item("숫돌",3)
}

enemys = {
    "새새색": Enemy("새새색",spr_char1[0],8,weapons["쪼기"],3),
    "배애앰": Enemy("배애앰",spr_char1[1],10,weapons["뱀꼬리"]),
    "장난질": Enemy("장난질",spr_char1[2],12,weapons["부메랑"]),
    "직각": Enemy("직각",spr_mainChar1[2],30,weapons["구구단검"],3),
    "마르": Enemy("마르",spr_mainChar1[3],30,weapons["나누창"],3)
}

stamps = {
    "deathCircle": Stamp((0,0),1)
}

#region 메뉴관련 변수들

curMenu = "Main"

mainItems = []
upperItems = []
downerItems = []

mainCurser = 0
upperCurser = 0
downerCurser = 0

menuAble = False

#endregion

battleManager = BattleManager()
progressBar = ProgressBar()
curBattle = Battle("a",Weapon(",",0,0))

background_list = []

background_list.append(BackGround(stage1Bg[0],1,0))
background_list.append(BackGround(stage1Bg[1],3,0))
background_list.append(BackGround(stage1Bg[2],5,0))
background_list.append(BackGround(stage1Bg[3],10,0))
background_list.append(BackGround(stage1Bg[4],10,0))

player_tri = Player("삼각",spr_mainChar1[0],10)
player_rect = Player("지사",spr_mainChar1[1],10)

game_player = player_tri

game_lobby = True
game_start = False

render = 0
stamp_list = []



screenCount = 0
gameReset = False
def reset():
    global battleManager, progressBar, curBattle, background_list, player_tri, player_rect,game_player,game_lobby,game_start,render,stamp_list,screenCount,gameReset
    global curMenu, mainItems, upperItems, downerItems, menuAble
    curMenu = "Main"
    mainItems = []
    upperItems = []
    downerItems = []
    menuAble = False
    battleManager = BattleManager()
    progressBar = ProgressBar()
    curBattle = Battle("a",Weapon(",",0,0))

    background_list = []

    background_list.append(BackGround(stage1Bg[0],1,0))
    background_list.append(BackGround(stage1Bg[1],3,0))
    background_list.append(BackGround(stage1Bg[2],5,0))
    background_list.append(BackGround(stage1Bg[3],10,0))
    background_list.append(BackGround(stage1Bg[4],10,0))

    player_tri = Player("삼각",spr_mainChar1[0],10)
    player_rect = Player("지사",spr_mainChar1[1],10)

    player_tri.giveWeapon(weapons["플러스검"])
    player_rect.giveWeapon(weapons["마너스검"])

    game_player = player_tri

    game_lobby = True
    game_start = False

    render = 0
    stamp_list = []

    screenCount = 0
    gameReset = False   


def play_game():
    #region 기초 변수 초기화

    #region 기본변수
    reset()
    global game_start
    global menuAble
    global screenCount
    global curMenu
    global screen
    global keys
    global fullscreen
    global mainItems
    global upperItems
    global downerItems
    global mainCurser
    global upperCurser
    global downerCurser
    global curBattle
    global render
    global gameReset
    global game_lobby
    screenCount = 0
    gameReset = False
    game_lobby = True
    game_start = False
    playing = True
    prev_time = 0
    fullscreen = False
    count = 0
    bgx = 0


    loading = True

    menuAble = False

    save_upper = 0
    battleStart = False
    #endregion

    # region 메인관련변수
    selectbox = Rect(0,0,0,0)
    #endregion

    # region 게임 자원들 초기화
    mainItems.append(LobbyItem("게임",["플러스워드","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"],menu_icon[0]))
    mainItems.append(LobbyItem("설정",["게임설정","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"],menu_icon[1]))
    upperItems = [MainItem(0,"매뉴얼",["수학으로 죽고사는 게임"],menu_icon[2]),MainItem(1,"캐릭터 설정",["수학으로 죽고사는 게임"],menu_icon[3]),\
        MainItem(2,"쉬움",["수학으로 죽고사는 게임"],menu_icon[4]),MainItem(3,"보통",["수학으로 죽고사는 게임"],menu_icon[5]),MainItem(4,"어려움",["수학으로 죽고사는 게임"],menu_icon[6])]
    downerItems =  [MainItem(5,"배경음 ▲",["수학으로 죽고사는 게임"],menu_icon[7]),MainItem(6,"배경음 ▼",["수학으로 죽고사는 게임"],menu_icon[8]),\
        MainItem(7,"효과음 ▲",["수학으로 죽고사는 게임"],menu_icon[9]),MainItem(8,"효과음 ▼",["수학으로 죽고사는 게임"],menu_icon[10]),MainItem(9,"화면설정",["수학으로 죽고사는 게임"],menu_icon[11])]

    render = mainItems[0]
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
        keys["0"] = False
        keys["1"] = False
        keys["2"] = False
        keys["3"] = False
        keys["4"] = False
        keys["5"] = False
        keys["6"] = False
        keys["7"] = False
        keys["8"] = False
        keys["9"] = False
        keys["minus"] = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 게임끄기
                playing = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN: 
                
                keys["up"] = event.key == pygame.K_KP8
                keys["down"] = event.key == pygame.K_KP5 or event.key == pygame.K_KP2
                keys["left"] = event.key == pygame.K_KP4 
                keys["right"] = event.key == pygame.K_KP6  
                keys["enter"] = event.key == pygame.K_KP_ENTER
                keys["back"] = event.key == pygame.K_KP_PERIOD or event.key == pygame.K_BACKSPACE
                keys["0"] = event.key == pygame.K_KP0
                keys["1"] = event.key == pygame.K_KP1
                keys["2"] = event.key == pygame.K_KP2
                keys["3"] = event.key == pygame.K_KP3
                keys["4"] = event.key == pygame.K_KP4
                keys["5"] = event.key == pygame.K_KP5
                keys["6"] = event.key == pygame.K_KP6
                keys["7"] = event.key == pygame.K_KP7
                keys["8"] = event.key == pygame.K_KP8
                keys["9"] = event.key == pygame.K_KP9
                keys["minus"] = event.key == pygame.K_KP_MINUS
                if event.key == K_F4: setFullScreen()

        if(menuAble):
            if curMenu == "Upper":
                
                if keys["left"]:
                    curMenu = "Main"                    
                    render = mainItems[mainCurser]
                    if battleManager.itemEquip: battleManager.itemEquip = False
                if keys["right"]:
                    if battleManager.item_get:
                        if(upperItems[upperCurser].__class__.__name__ == "Weapon"):
                            battleManager.player.giveWeapon(upperItems[upperCurser])
                        elif(upperItems[upperCurser].__class__.__name__ == "Item"):
                            battleManager.player.giveItem(upperItems[upperCurser])
                        upperItems = battleManager.player.weapon
                        battleManager.item_get = False
                    elif battleManager.itemEquip:
                        downerItems[downerCurser].equip_active(upperItems[upperCurser])
                        battleManager.itemEquip = False
                        curMenu = "Downer"
                        upperCurser = save_upper
                        mainCurser = 1
                        if(len(downerItems) <=0):
                            curMenu = "Main"

                    else:
                        upperItems[upperCurser].active() # 아이템 발동
                if keys["up"]:
                    upperCurser -= 1
                    if upperCurser < 0: upperCurser = len(upperItems)-1
                    render = upperItems[upperCurser]
                if keys["down"]:
                    upperCurser += 1
                    if upperCurser >= len(upperItems):  upperCurser = 0 
                    render = upperItems[upperCurser]
            
            elif curMenu == "Downer":
                try:
                    if downerCurser > len(downerItems): downerCurser = len(downerItems)-1
                    if keys["left"]:
                        curMenu = "Main"
                        render = mainItems[mainCurser]
                    if keys["right"]:
                        downerItems[downerCurser].active() # 아이템 발동
                        
                        if not game_lobby:
                            if downerItems[downerCurser].equip:
                                battleManager.itemEquip = True
                                save_upper = upperCurser
                                upperCurser = 0
                            if(len(downerItems) <= 0):
                                curMenu = "Main"
                        
                    if keys["up"]:
                        downerCurser -= 1
                        if downerCurser < 0: downerCurser = len(downerItems)-1
                        render = downerItems[downerCurser]
                    if keys["down"]:
                        downerCurser += 1
                        if downerCurser >= len(downerItems): downerCurser = 0
                        render = downerItems[downerCurser]
                except IndexError:
                    print("downerError")
                    if(len(downerItems) <= 0):
                        curMenu = "Main"
                    downerCurser = 0
                    
            elif curMenu == "Main":
                if keys["right"]:
                    if(mainCurser == 0 and len(upperItems) > 0):
                        curMenu = "Upper"
                        render = upperItems[upperCurser]
                    elif(mainCurser == 1 and len(downerItems) > 0):
                        curMenu = "Downer"
                        render = downerItems[downerCurser]
                if keys["up"]:
                    mainCurser -= 1
                    if mainCurser < 0: mainCurser = 1
                    render = mainItems[mainCurser]
                if keys["down"]:
                    mainCurser += 1
                    if mainCurser > 1: mainCurser = 0
                    render = mainItems[mainCurser]













        



        #endregion
             
        #region 시작화면
        if game_lobby:
            downerItems[0].count = game_setting[2]
            downerItems[1].count = game_setting[2]
            downerItems[2].count = game_setting[3]
            downerItems[3].count = game_setting[3]
            game_player.update()            
        #endregion

        #region 게임
        if game_start and not loading: 
            #region 화면전환
            if(count == 0):   
                menuAble = False
            if(count < 160):
                bgx += 1
                count += 1
            if(count == 1):
                battleManager.player.idlespd =5
            if(count == 60):
                stamp_list.append(Stamp((0,0),2))
            if(count == 120):          
                battleManager.setEnemys()
                if len(battleManager.enemys) == 1:
                    battleManager.enemys[0].setMove(806,10)
                if len(battleManager.enemys) == 2:
                    battleManager.enemys[0].setMove(706,10)
                    battleManager.enemys[1].setMove(906,10)
                if len(battleManager.enemys) == 3:
                    battleManager.enemys[0].setMove(606,10)
                    battleManager.enemys[1].setMove(806,10)
                    battleManager.enemys[2].setMove(1006,10)
            if(count == 160):
                battleManager.player.idlespd =50
                menuAble = True
                if battleManager.itemEquip:
                    curMenu = "Upper"
                    mainCurser = 0

            if(len(battleManager.player_WeaponSlot) >= game_player.behavior and not battleStart):
                if keys["enter"]: # 커맨드 모두 입력시
                    battleManager.battleStart = True
                    progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
                if keys["back"]: 
                    battleManager.player_WeaponSlot = []
                    progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
            
            if(battleManager.battleStart): 
                battleManager.battle()
                if(len(battleManager.enemys) <= 0): # 적이 없을시
                    battleManager.item_get = True
                    battleManager.battleStart = False
                    mainCurser = 0
                    print("len(battleManager.enemys) <= 0")
                    save_upper = upperCurser
                    # count = 0

            if(battleManager.item_get):
                if count == 160:
                    stamp_list.append(Stamp((0,0),4))
                    battleManager.suffleItem()
                    upperItems = battleManager.randItems
                count += 1
                curMenu = "Upper"

            if(not battleManager.item_get and count > 160):
                print("not battleManager.item_get and count > 160")
                count = 0
                upperCurser = save_upper
                menuAble = False
                curMenu = "Main"

            #endregion           
            game_player.update()
            if(game_player.death): 
                count = 0
                game_start = False
            for enemy in battleManager.enemys:
                enemy.update()   
        if(game_start and loading):
            count += 1
            game_player.update()  
            curMenu = "Main"
            if(count == 10):
                game_player.pos = 144
                game_player.move_point = 144
                count = 0
                loading = False
        
        for stamp in stamp_list[:]:
            stamp.update()       
        
        if(game_player.death):
            if(count == 0):
                mainItems[0] = LobbyItem("모험")
                mainItems[1] = LobbyItem("끝!")
                upperItems = [MainItem(10,"메인으로",["쳐발림"],menu_icon[2]),MainItem(10,"돌아가서",["쳐발림"],menu_icon[2]),\
        MainItem(10,"잠깐",["쳐발림"],menu_icon[2]),MainItem(10,"쉬엇다가",["쳐발림"],menu_icon[2]),MainItem(10,"다시하자!",["쳐발림"],menu_icon[2])] 
                count += 1
            curMenu = "Upper"
            render = upperItems[upperCurser]
                          
        #endregion


        #region 그리기

        #region 기본
        screen.fill((0,0,0))
        menu_render.blit(menu,(-30,-30))
        battleMenu_render.blit(battleMenu,(0,0))
        submenu_x = 20
        submenu_y = 12
        #endregion
        
        #region 메인칸 텍스트
        text_color = (255, 255, 255)
        text = menuFont.render(mainItems[0].text,True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,90-text_rect.centery))
        text = menuFont.render(mainItems[1].text,True,text_color)
        text_rect = text.get_rect()
        menu_render.blit(text,(68-text_rect.centerx,270-text_rect.centery))
        #endregion
        
        #region 서브칸 텍스트
        if mainCurser == 0:
            a = 0
            for i in upperItems:
                text_color = (255, 255, 255)
                text = menuFont.render(i.name,True,text_color)
                
                b=0
                if(len(upperItems)>4):
                    b= upperCurser-2
                    if(upperCurser<3):
                        b = 0
                    if(upperCurser>len(upperItems)-3):
                        b = len(upperItems)-5
                menu_render.blit(text,(135+submenu_x,a*71+submenu_y-b*71))
                if className(i,"Weapon"):
                    drawText(menuFont,str(i.count),menu_render,446+submenu_x,a*71+submenu_y-b*71)
                    
                a += 1
        if mainCurser == 1:
            a = 0
            for i in downerItems:
                text_color = (255, 255, 255)
                text = menuFont.render(i.name,True,text_color)
                
                b = 0
                if(len(downerItems)>4):
                    b= downerCurser-2
                    
                    if(downerCurser<3):
                        b = 0
                    if(downerCurser>len(downerItems)-3):
                        b = len(downerItems)-5
                menu_render.blit(text,(135+submenu_x,a*71+submenu_y-b*71))
                if className(i,"MainItem"):
                    number = menuFont.render(str(i.count),True,text_color)
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
        for i in range(0,len(render.message)):            
            if(i==0): text = capitextFont.render(render.message[i],True,text_color)
            else:text = textFont.render(render.message[i],True,text_color)
            text_rect = text.get_rect()
            menu_render.blit(text,(770-text_rect.centerx,226+i*30))
        menu_render.blit(render.icon,(710,39)) 
        if className(render,"Weapon"):
            drawText(menuFont,"Next "+str(render.max_exp),menu_render,560+50,69)
            drawText(menuFont,"Exp "+str(render.exp),menu_render,560+50,144)
            drawText(menuFont,"Lv "+str(render.count),menu_render,887+50,69)
            drawText(menuFont,"Dmg "+str(render.damage),menu_render,887+50,144)
        #endregion
        
        #region 전투중일때 그리기
        if(battleManager.battleStart):
            
            battleManager.battle_Chain[0].draw(battleMenu_render)
            screen.blit(battleMenu_render,(0,0))
        #endregion

        #region 메뉴,바닥,배경 그리기 

        if(len(background_list) > 0):
            for img in background_list:
                img.draw(bgx)  
            
             
        screen.blit(menu,(0,0))
        screen.blit(menu_render,(30,30))


        if(battleManager.battleStart):            
            draw_rect_alpha(screen,(0,0,0,100),Rect(0,0,1080,720))
        progressBar.draw(screen)     
        if(battleManager.battleStart):            
            screen.blit(battleMenu_render,(0,0))
        
        #endregion
        

        #region 캐릭터, 적 , 효과 그리기
        for stamp in stamp_list:
            stamp.draw(screen)
        game_player.draw(screen)
        for enemy in battleManager.enemys:
            enemy.draw(screen)
        #endregion
        
        #endregion
        if(screenCount > 0):
            screen.blit(screen,(rndNum(-25,25),rndNum(-25,25)))
            screenCount -= 1

        if gameReset: break
        pygame.display.flip() 

    play_game()


def drawText(font,text,screen,x,y,color=(255,255,255)):
    number = font.render(text,True,color) 
    number_rect = number.get_rect()
    screen.blit(number,(x-number_rect.centerx,y))
















def gameStart():
    global menuAble
    global game_start
    global game_lobby
    global game_player
    global upperItems
    global downerItems
    global mainCurser
    global upperCurser
    global downerCurser
    global curMenu
    global render
    game_player.setMove(1080,10)
    game_start = True
    game_lobby = False
    mainItems[0] = LobbyItem("전투",["전투","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"], menu_icon[0])
    mainItems[1] = LobbyItem("아이템",["아이템","게임을 시작합니다","그리고 끔찍한 악몽이 시작됩니다"], menu_icon[1]  )
    upperItems = game_player.weapon
    downerItems = game_player.item

    render = mainItems[0]

    mainCurser = 0
    upperCurser = 0
    downerCurser = 0
    
    battleManager.stage1.preSetStage()

    menuAble = True
    battleManager.player = game_player

if __name__ == "__main__":
    play_game()

