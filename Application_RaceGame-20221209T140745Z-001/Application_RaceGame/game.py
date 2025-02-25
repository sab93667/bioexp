import pygame, random, sys ,os,time
from pygame.locals import *

import time
import serial
import threading
from collections import Counter
import numpy as np
from scipy import signal
from tensorflow import keras
import model

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
FPS = 40
BADDIEMINSIZE = 10
BADDIEMAXSIZE = 20
BADDIEMINSPEED = 3
BADDIEMAXSPEED = 4
ADDNEWBADDIERATE = 35
PLAYERMOVERATE = 2
count=3

moveLeft = False
moveRight = False
moveUp = False
moveDown = False

def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN and event.key == ord('s'):
                if event.key == K_ESCAPE: #escape quits
                    terminate()
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def checkgesture(RF):
    global moveLeft
    global moveRight
    global moveUp
    global moveDown
    while RF.is_set():
        time.sleep(0.001)
        temp = LIST
        print(temp)
        if temp[-1] == 7 and temp[-2] == 7 :
            moveRight = False
            moveLeft = True
            time.sleep(0.5)
            moveLeft = False
            time.sleep(0.5)
        elif temp[-1] == 6 and temp[-2] == 6 :
            moveLeft = False
            moveRight = True
            time.sleep(0.5)
            moveRight = False
            time.sleep(0.5)
        elif temp[-1] == 4 and temp[-2] == 4 :
            moveDown = False
            moveUp = True
            time.sleep(0.5)
            moveUp = False
            time.sleep(0.5)
        elif temp[-1] == 5 and temp[-2] == 5 :
            moveUp = False
            moveDown = True
            time.sleep(0.5)
            moveDown = False
            time.sleep(0.5)
        elif temp[-1] == 0 and temp[-2] == 0 :
            moveLeft = False
            moveRight = False
            moveUp = False
            moveDown = False
            time.sleep(0.2)
        


# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('car race')
pygame.mouse.set_visible(False)

# fonts
font = pygame.font.SysFont(None, 30)

# images
playerImage = pygame.image.load('image/car1.png')
car3 = pygame.image.load('image/car3.png')
car4 = pygame.image.load('image/car4.png')
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('image/car2.png')
sample = [car3,car4,baddieImage]
wallLeft = pygame.image.load('image/left.png')
wallRight = pygame.image.load('image/right.png')

###==============================================================###
gestures = {0:"rest",
            1:"剪刀",
            2:"石頭",
            3:"布",
            4:"手腕:上",
            5:"手腕:下",
            6:"手腕:內",
            7:"手腕:外",
            8:"大拇指",
            9:"雙點"}

COM_PORT = 'COM7'    # 指定通訊埠名稱
BAUD_RATES = 500000    # 設定傳輸速率'''
LIST = [0] * 6

RF = threading.Event()
KL = threading.Lock()

model_thread = threading.Thread(target = model.main, args=(KL, RF, COM_PORT, BAUD_RATES, LIST,))

RF.set()
model_thread.setDaemon(True)
model_thread.start()

###==============================================================###

# "Start" screen
drawText('Press s to start the game.', font, windowSurface, (WINDOWWIDTH / 3) , (WINDOWHEIGHT / 3))
pygame.display.update()
waitForPlayerToPressKey()
zero=0
if not os.path.exists("data/save.dat"):
    f=open("data/save.dat",'w')
    f.write(str(zero))
    f.close()   
v=open("data/save.dat",'r')
topScore = int(v.readline())
v.close()

checker = threading.Thread(target = checkgesture, args=(RF,))
checker.setDaemon(True)
checker.start()
while (count>0):
    # start of the game
    baddies = []
    score = 0
    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0
    
    try:
        
        while True: # the game loop
            score += 1 # increase score
            for event in pygame.event.get():
                
                if event.type == QUIT:
                    terminate()
    
                if event.type == KEYDOWN:
                    if event.key == ord('z'):
                        reverseCheat = True
                    if event.key == ord('x'):
                        slowCheat = True
                    if event.key == K_LEFT or event.key == ord('a'):
                        moveRight = False
                        moveLeft = True
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveLeft = False
                        moveRight = True
                    if event.key == K_UP or event.key == ord('w'):
                        moveDown = False
                        moveUp = True
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveUp = False
                        moveDown = True
    
                if event.type == KEYUP:
                    if event.key == ord('z'):
                        reverseCheat = False
                        score = 0
                    if event.key == ord('x'):
                        slowCheat = False
                        score = 0
                    if event.key == K_ESCAPE:
                            terminate()
                
    
                    if event.key == K_LEFT or event.key == ord('a'):
                        moveLeft = False
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveRight = False
                    if event.key == K_UP or event.key == ord('w'):
                        moveUp = False
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveDown = False
    
                
    
            # Add new baddies at the top of the screen
            if not reverseCheat and not slowCheat:
                baddieAddCounter += 1
            if baddieAddCounter == ADDNEWBADDIERATE:
                baddieAddCounter = 0
                baddieSize =30 
                newBaddie = {'rect': pygame.Rect(random.randint(140, 485), 0 - baddieSize, 23, 47),
                            'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                            'surface':pygame.transform.scale(random.choice(sample), (23, 47)),
                            }
                baddies.append(newBaddie)
                sideLeft= {'rect': pygame.Rect(0,0,126,600),
                           'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                           'surface':pygame.transform.scale(wallLeft, (126, 599)),
                           }
                baddies.append(sideLeft)
                sideRight= {'rect': pygame.Rect(497,0,303,600),
                           'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                           'surface':pygame.transform.scale(wallRight, (303, 599)),
                           }
                baddies.append(sideRight)
                
                
    
            # Move the player around.
            if moveLeft and playerRect.left > 0:
                playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
            if moveRight and playerRect.right < WINDOWWIDTH:
                playerRect.move_ip(PLAYERMOVERATE, 0)
            if moveUp and playerRect.top > 0:
                playerRect.move_ip(0, -1 * PLAYERMOVERATE)
            if moveDown and playerRect.bottom < WINDOWHEIGHT:
                playerRect.move_ip(0, PLAYERMOVERATE)
            
            for b in baddies:
                if not reverseCheat and not slowCheat:
                    b['rect'].move_ip(0, b['speed'])
                elif reverseCheat:
                    b['rect'].move_ip(0, -5)
                elif slowCheat:
                    b['rect'].move_ip(0, 1)
    
             
            for b in baddies[:]:
                if b['rect'].top > WINDOWHEIGHT:
                    baddies.remove(b)
    
            # Draw the game world on the window.
            windowSurface.fill(BACKGROUNDCOLOR)
    
            # Draw the score and top score.
            drawText('Score: %s' % (score), font, windowSurface, 128, 0)
            drawText('Top Score: %s' % (topScore), font, windowSurface,128, 20)
            drawText('Rest Life: %s' % (count), font, windowSurface,128, 40)
            
            windowSurface.blit(playerImage, playerRect)
    
            
            for b in baddies:
                windowSurface.blit(b['surface'], b['rect'])
    
            pygame.display.update()
    
            # Check if any of the car have hit the player.
            if playerHasHitBaddie(playerRect, baddies):
                if score > topScore:
                    g=open("data/save.dat",'w')
                    g.write(str(score))
                    g.close()
                    topScore = score
                break
    
            mainClock.tick(FPS)
    
        # "Game Over" screen.
        count=count-1
        time.sleep(1)

        if (count==0):
            drawText('Game over', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
            drawText('Press any key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 30)
            pygame.display.update()
            time.sleep(2)
            waitForPlayerToPressKey()
            count=3
     
    except (KeyboardInterrupt, SystemExit):
        RF.clear()
        model_thread.join()
        checker.join()
        print ('KeyboardInterrupt')
        
