
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
        self.index = -1
        self.num = num
        self.enemys = enemys
        self.enemy_line = []
        self.preSetStage()
    def preSetStage(self):
        if self.num == 1:
            self.enemy_line = [
                [self.enemys[0]],[self.enemys[1]],[self.enemys[2]],[self.enemys[rndNum(0,2)],self.enemys[rndNum(0,2)]],[self.enemys[3]],\
                    [self.enemys[0]],[self.enemys[1]],[self.enemys[2]],[self.enemys[rndNum(0,2)],self.enemys[rndNum(0,2)]],[self.enemys[3]]
            ]


    def getEnemy(self):
        self.index += 1
        return self.enemy_line[self.index]


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
        self.damage = 5
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
        self.dmgList = []

        self.preSetWeapon()


    def active(self):
        global battleManager
        if(len(battleManager.player_WeaponSlot) < game_player.behavior):
            battleManager.addPlayerWeaponSlot(self)
            progressBar.updateProgress(battleManager.player_WeaponSlot,battleManager.player.behavior)
    def preSetWeapon(self):
        if self.id == 1:
            self.rndList = [(1,9),(10,20),(60,100),(50,200)]
            self.dmgList = [1,2,4,8]


    def getWeapon(self):
        self.damage = 0
        if self.id == 1:
            self.damage = self.dmgList[self.count]
            a = rndTup(self.rndList[self.count])
            b = rndTup(self.rndList[self.count])
            c = a + b
            question = [Num(a),Sim("+"),Num(b),Sim("="),Num(c)]
            answer = [4]
            return question, answer
        if self.id == 2:
            self.damage = 1
            a = rndNum(1,9)
            b = rndNum(1,9)
            c = a - b
            question = [Num(a),Sim("-"),Num(b),Sim("="),Num(c)]
            answer = [4]
            return question, answer
        if self.id == 3:
            self.damage = 1
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
            return question, answer
        if self.id == 4:
            self.damage = 1
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
            return question, answer
        if self.id == 5:
            self.damage = 1
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
            return question, answer













    def levelRndNum(self):
        rndNum(1,9)

    def levelUp(self):
        self.exp = 0
        self.count += 1
        self.max_exp = self.lvUpList[self.count]

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
            battleManager.player.health += 5
            battleManager.player.item.remove(self)
        if(self.id == 2):
            self.equip = True
    def equip_active(self,weapon):
        if self.id == 2:
            weapon.levelUp()
        battleManager.player.item.remove(self)


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

class Enemy:
    def __init__(self,name,sprite,health,weapon = Weapon("",0,0)):
        self.tag = "Enemy"
        self.pos = 1100
        self.saved_pos = 0
        self.name = name

        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        self.sprite = sprite
        self.health = health
        self.max_health = self.health
        self.weapon = copy(weapon)
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
        self.randItems.append(copy(items["간식"]))
        self.randItems.append(copy(weapons["마너스검"]))
        self.randItems.append(copy(weapons["쪼기"]))
        self.randItems.append(copy(weapons["부메랑"]))
        

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
        global keys
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
                        self.defend.health -=  self.weapon.damage
                        self.attack.setMove(540-CENTERDIS-knockback,10)
                        self.defend.setMove(540+CENTERDIS+knockback,10)
                    if(self.defend.tag == "Player"):
                        self.attack.condition = 3
                        self.defend.condition = 3
                        if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul:
                            self.attack.health -=  math.ceil(self.weapon.damage/2)
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
                if not self.failed:
                    enemy = self.attack if self.attack.tag == "Enemy" else self.defend
                    if enemy.health <= 0:
                        del battleManager.enemys[0]
                        for battle in battleManager.battle_Chain[:]:
                            if(battle.attack == self.defend):
                                battleManager.battle_Chain.remove(battle)
                        if(len(battleManager.enemys) <= 0):
                            battleManager.battle_Chain = []
                    
                        
        else:
            self.inputNum()
            self.weapon.time -= 1
        #endregion
                

        #region 전투끝
        if(self.weapon.time <= 0 and not self.delay):   

            if not self.bool:
                self.originWeapon.exp += 1
                if self.originWeapon.exp >= self.originWeapon.max_exp: 
                    self.originWeapon.levelUp()
                
                if(self.attack.tag == "Enemy"):
                    self.attack.condition = 3
                    self.defend.condition = 4
                    self.defend.health -=  self.weapon.damage
                    self.attack.setMove(540+CENTERDIS+knockback//2,10)
                    self.defend.setMove(540-CENTERDIS-knockback//2,10)

                if(self.defend.tag == "Enemy"):
                    self.attack.condition = 4
                    self.defend.condition = 3
                    # if self.weapon.time > self.weapon.max_time - self.weapon.max_time/battleManager.player.time_beul:
                    #     self.weapon.damage *= 2
                    self.attack.health -=  math.ceil(self.weapon.damage/2)
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
    "간식": Item("간식",2)
}

enemys = {
    "새새색": Enemy("새새색",spr_char1[0],1,weapons["쪼기"]),
    "배애앰": Enemy("배애앰",spr_char1[1],10,weapons["뱀꼬리"]),
    "장난질": Enemy("장난질",spr_char1[2],12,weapons["부메랑"]),
    "직각": Enemy("직각",spr_mainChar1[2],30,weapons["구구단검"]),
    "마르": Enemy("마르",spr_mainChar1[3],30,weapons["나누창"])
}

#region 메뉴관련 변수들

curMenu = "Main"
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
player_rect = Player("지사",spr_mainChar1[1],9)

player_tri.giveItem(items["간식"])
player_tri.giveItem(items["간식"])
player_tri.giveItem(items["간식"])
player_tri.giveWeapon(weapons["플러스검"])

game_player = player_tri

game_lobby = True
game_start = False


def play_game():
    #region 기초 변수 초기화

    #region 기본변수
    global menuAble
    global curMenu
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

    bgx = 0


    loading = True

    menuAble = False

    save_upper = 0
    battleStart = False
    #endregion

    # region 메인관련변수

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
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
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
                        mainCurser = 1
                        if(len(downerItems) <=0):
                            curMenu = "Main"

                    else:
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
            elif curMenu == "Downer":
                if keys["left"]:
                    curMenu = "Main"
                    render_message = mainDownVisual["message"] if mainCurser == 1 else mainUpVisual["message"]
                    render_icon = mainDownVisual["icon"] if mainCurser == 1 else mainUpVisual["icon"]
                if keys["right"]:
                    downerItems[downerCurser].active() # 아이템 발동
                    if downerItems[downerCurser].equip:
                        battleManager.itemEquip = True
                    if(len(downerItems) <= 0):
                        curMenu = "Main"
                    
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
            elif curMenu == "Main":
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
            if(count == 0):   
                menuAble = False
            if(count < 160):
                bgx += 1
                count += 1
            if(count == 1):
                battleManager.player.idlespd =5
            if(count == 60):
                print("적 출현!")
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
                    print("doing")
                    curMenu = "Upper"
                    upperCurser = 0
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
                    save_upper = upperCurser
                    # count = 0

            if(battleManager.item_get):
                if count == 160:
                    battleManager.suffleItem()
                    upperItems = battleManager.randItems
                count += 1
                curMenu = "Upper"

            if(not battleManager.item_get and count > 160):
                count = 0
                upperCurser = save_upper
                menuAble = False
                curMenu = "Main"




            #endregion           
            game_player.update()
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
        
        #region 캐릭터, 적 그리기
        game_player.draw(screen)
        for enemy in battleManager.enemys:
            enemy.draw(screen)
        #endregion
        
        #endregion

        pygame.display.flip() 



















def gameStart():
    global menuAble
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
    global curMenu
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










if __name__ == "__main__":
    play_game()

