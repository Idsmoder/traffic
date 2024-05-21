import random
import time
import threading
import pygame
import sys
import os

# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultRed = 150
defaultYellow = 5

signals = []
noOfSignals = 4
greenSingals = [[0, 2], [1, 3]]
currentGreen = [0, 2]  # Hozirda qaysi signal yashil ekanligini ko'rsatadi
nextGreen = [1, 3]  # Qaysi signal keyingi yashil rangga aylanishini bildiradi
currentYellow = []  # Sariq signal yoqilgan yoki o'chirilganligini bildiradi

speeds = {'car': 0.8, 'bus': 0.5, 'truck': 0.5, 'bike': 0.8}  # transport vositalarining o'rtacha tezligi


# Coordinates of vehicles' start
x = {'right': [0, 0, 0, 0], 'down': [652, 613, 573, 533], 'left': [1400, 1400, 1400, 1400], 'up': [725, 765, 805, 845]}
y = {'right': [478, 520, 562, 604], 'down': [0, 0, 0, 0], 'left': [410, 368, 328, 288], 'up': [800, 800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [],3:[], 'crossed': 0, 'uncrossed':0, 'turnCrossed': 0}, 'down': {0: [], 1: [], 2: [],3:[], 'crossed': 0, 'uncrossed':0, 'turnCrossed': 0},
            'left': {0: [], 1: [], 2: [],3:[], 'crossed': 0, 'uncrossed':0, 'turnCrossed': 0}, 'up': {0: [], 1: [], 2: [],3:[], 'crossed': 0, 'uncrossed':0, 'turnCrossed': 0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(480, 640), (490, 190), (880, 190), (880, 640)]
signalTimerCoods = [(490, 672), (500, 225), (890, 225), (890, 672)]

# Coordinates of stop lines
stopLines = {'right': 455, 'down': 220, 'left': 940, 'up': 710}
defaultStop = {'right': 450, 'down': 210, 'left': 960, 'up': 715}

# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25   # moving gap

# set allowed vehicle types here
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {0:[], 1:[], 2:[], 3:[]}, 'down': {0:[], 1:[], 2:[], 3:[]}, 'left': {0:[], 1:[], 2:[], 3:[]}, 'up': {0:[], 1:[], 2:[], 3:[]}}
vehiclesNotTurned = {'right': {0:[], 1:[], 2:[], 3:[]}, 'down': {0:[], 1:[], 2:[], 3:[]}, 'left': {0:[], 1:[], 2:[], 3:[]}, 'up': {0:[], 1:[], 2:[], 3:[]}}
rotationAngle = 3
mid = {'right': {'x':550, 'y':445}, 'down': {'x':650, 'y':320}, 'left': {'x':850, 'y':425}, 'up': {'x':650, 'y':620}}
# set random or default green signal time here 
randomGreenSignalTimer = False
# set random green signal time range here 
randomGreenSignalTimerRange = [10,20]

timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (1100,50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(490, 725), (500, 170), (890, 170), (890, 725)]

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.uncrossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
         
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):   
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().width 
                - stoppingGap
                
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().width 
                + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().height 
                - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().height 
                + stoppingGap
        else:
            self.stop = defaultStop[direction]
            
        # Set new starting and stopping coordinate
        if(direction=='right'):
            temp = self.image.get_rect().width + stoppingGap 
               
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        
        if(self.direction=='right'):
            if(self.uncrossed==0 and self.y<300):
                self.uncrossed = 1
                vehicles[self.direction]['uncrossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 0):
                    if(self.crossed==0 or self.x+self.image.get_rect().width<stopLines[self.direction]+290):
                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):               
                            if(self.x <650):
                                self.x += self.speed
                            if((vehicles['left']['uncrossed']==vehicles['left']['crossed']) or vehicles['left']['crossed']==0):
                                self.x += self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.1
                            self.y -= 1.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif(self.lane == 3):
                    if(self.crossed==0 or self.x+self.image.get_rect().width<mid[self.direction]['x']):

                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                 
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1.1
                            self.y += 1.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.y+self.image.get_rect().height)<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):
                                self.y += self.speed
            else:
                

                if(self.crossed == 0):
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                        self.x += self.speed

                else:
                    if((self.crossedIndex==0) or (self.x+self.image.get_rect().width<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):                 
                        self.x += self.speed
        elif(self.direction=='down'):
            if(self.uncrossed==0 and self.x>800):
                self.uncrossed = 1
                vehicles[self.direction]['uncrossed'] += 1
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 0):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<stopLines[self.direction]+280):
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            if(self.y <470):
                                self.y += self.speed
                            if(vehicles['up']['uncrossed']==vehicles['up']['crossed'] or vehicles['up']['crossed']==0):
                                self.y += self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 0.1
                            self.y += 0.1
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.x + self.image.get_rect().width) < (vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):
                                self.x += self.speed
                elif(self.lane == 3):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<mid[self.direction]['y']):
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))): 
                                self.x -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                        self.y += self.speed
                else:
                    if((self.crossedIndex==0) or (self.y+self.image.get_rect().height<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):                
                        self.y += self.speed
        elif(self.direction=='left'):
            if(self.uncrossed==0 and self.x<610):
                self.uncrossed = 1
                vehicles[self.direction]['uncrossed'] += 1
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn !=1):
                    vehicles[self.direction]['turnCrossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 0):
                    if(self.crossed==0 or self.x>stopLines[self.direction]-70):
                        if((self.x>=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else: 
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 8
                            self.y += 1.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.y + self.image.get_rect().height) <(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y  -  movingGap))):
                                self.y += self.speed
                elif(self.lane == 3):
                    if(self.crossed==0 or self.x>mid[self.direction]['x']):
                        if((self.x>=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height +  movingGap))):
                                self.y -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x>=self.stop or (currentGreen == [0, 2] and currentYellow != currentGreen)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.x>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
            
                            
        
        elif(self.direction=='up'):
            if(self.uncrossed==0 and self.y<470):
                self.uncrossed = 1
                vehicles[self.direction]['uncrossed'] += 1
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 0):
                    if(self.crossed==0 or self.y>stopLines[self.direction]-60):
                        if((self.y>=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 10.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif(self.lane == 3):
                    if(self.crossed==0 or self.y>mid[self.direction]['y']):
                        if((self.y>=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y>=self.stop or (currentGreen == [1, 3] and currentYellow != currentGreen)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.y>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed 

# Initialization of signals with default values
def initialize():
    
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.yellow+ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()

 

def repeat():
    global currentGreen, currentYellow, nextGreen
    while (signals[currentGreen[0]].green > 0 and signals[currentGreen[1]].green > 0):   # joriy yashil signalning taymeri nolga teng emas
        updateValues()
        time.sleep(1)
    if currentYellow == 0:
        currentYellow = []  # sariq signalni o'chiring
    else:
        currentYellow = [currentGreen[0],currentGreen[1]]   # sariq signalni yoqing
    # chiziqlar va transport vositalarining to'xtash koordinatalarini tiklash 
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[currentGreen[0]]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen[0]]]
    while(signals[currentGreen[0]].yellow > 0 and signals[currentGreen[1]].yellow > 0):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(1)
    if currentYellow == 0:
        currentYellow = []  # sariq signalni o'chiring
    else:
        currentYellow = [currentGreen[0],currentGreen[1]]   # sariq signalni yoqing
    
    
    # joriy signalning barcha signal vaqtlarini standart/tasodifiy vaqtga qaytaring
    signals[currentGreen[0]].green = defaultGreen[0]
    signals[currentGreen[1]].green = defaultGreen[0]
    signals[currentGreen[0]].yellow = defaultYellow
    signals[currentGreen[1]].yellow = defaultYellow
    signals[currentGreen[0]].red = defaultRed
    signals[currentGreen[1]].red = defaultRed
       
    currentGreen = nextGreen  # keyingi signalni yashil signal sifatida o'rnating
    if currentGreen == [0, 2]:
        nextGreen = [1, 3]
    else:
        nextGreen = [0, 2]  # keyingi yashil signalni o'rnating
    signals[nextGreen[0]].red = signals[currentGreen[0]].yellow + signals[
        currentGreen[0]].green  # keyingi signalning qizil vaqtini keyingi signalning (sariq vaqt + yashil vaqt) sifatida belgilang
    signals[nextGreen[1]].red = signals[currentGreen[1]].yellow + signals[
        currentGreen[1]].green  # keyingi signalning qizil vaqtini keyingi signalning (sariq vaqt + yashil vaqt) sifatida belgilang
    repeat()

# Signal taymerlarining qiymatlarini har soniyadan keyin yangilang
def updateValues():
    for i in greenSingals:
        if i == currentGreen:
            
            if signals[i[0]].green == 0 and signals[i[1]].green == 0:
                signals[i[0]].yellow -= 1
                signals[i[1]].yellow -= 1
            else:
                signals[i[1]].green -= 1
                signals[i[0]].green -= 1
        else:
            signals[i[0]].red -= 1
            signals[i[1]].red -= 1

# Simulyatsiyada transport vositalarini yaratish
def generateVehicles():
    while(True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(0,3)
        will_turn = 0
        temp = random.randint(0,99)
        direction_number = 0
        dist = [25,50,75,100]
        if(temp<dist[0]):
            direction_number = 0
            if(lane_number == 0):
                will_turn = 1
            elif(lane_number == 3):
                will_turn = 1
        elif(temp<dist[1]):
            direction_number = 1
            if(lane_number == 0):
                will_turn = 1
            elif(lane_number == 3):
                will_turn = 1
        elif(temp<dist[2]):
            direction_number = 2
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.3)

def showStats():
    totalVehicles = 0
    print('Direction-wise Vehicle Counts')
    for i in range(0,4):
        if(signals[i]!=None):
            print('Direction',i+1,':',vehicles[directionNumbers[i]]['crossed'])
            totalVehicles += vehicles[directionNumbers[i]]['crossed']
    print('Total vehicles passed:',totalVehicles)
    print('Total time:',timeElapsed)
def simTime():
    global timeElapsed, simulationTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simulationTime):
            showStats()
            os._exit(1) 

class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if(allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/choraxa.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="simTime",target=simTime, args=()) 
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showStats()
                sys.exit()

        screen.blit(background,(0,0))   # display background in simulation
        

        for i in greenSingals:
            if i == currentGreen:
                if signals[i[0]].green == 0 and signals[i[1]].green == 0:
                    screen.blit(yellowSignal, signalCoods[i[0]])
                    screen.blit(yellowSignal, signalCoods[i[1]])
                    signals[i[0]].signalText = signals[i[0]].yellow
                    signals[i[1]].signalText = signals[i[1]].yellow
                else:
                    screen.blit(greenSignal, signalCoods[i[0]])
                    screen.blit(greenSignal, signalCoods[i[1]])
                    signals[i[0]].signalText = signals[i[0]].green
                    signals[i[1]].signalText = signals[i[1]].green
            else:
                screen.blit(redSignal, signalCoods[i[0]])
                screen.blit(redSignal, signalCoods[i[1]])
                signals[i[0]].signalText = "-"
                signals[i[1]].signalText = "-"
                            
        signalTexts = ["","","",""]

        # display signal timer
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i])

        # display vehicle count
        for i in range(0,noOfSignals):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i],vehicleCountCoods[i])

        # display time elapsed
        timeElapsedText = font.render(("Vaqt o'tdi: "+str(timeElapsed) ), True, black, white)
        screen.blit(timeElapsedText,timeElapsedCoods)

        # display the vehicles
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
            
        pygame.display.update()


Main()