import random
import time
import threading
import pygame
import sys

# Signal taymerlarining standart qiymatlari
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 15
defaultYellow = 3
YellowSeconds = 3

signals = []
noOfSignals = 4
greenSingals = [[0, 2], [1, 3]]
currentGreen = [0, 2]  # Hozirda qaysi signal yashil ekanligini ko'rsatadi
nextGreen = [1, 3]  # Qaysi signal keyingi yashil rangga aylanishini bildiradi
currentYellow = []  # Sariq signal yoqilgan yoki o'chirilganligini bildiradi

speeds = {'car': 0.8, 'bus': 0.5, 'truck': 0.5, 'bike': 0.8}  # transport vositalarining o'rtacha tezligi

# Avtotransportni ishga tushirish koordinatalari
x = {'right': [0, 0, 0, 0], 'down': [652, 613, 573, 533], 'left': [1400, 1400, 1400, 1400], 'up': [725, 765, 805, 845]}
y = {'right': [478, 520, 562, 604], 'down': [0, 0, 0, 0], 'left': [410, 368, 328, 288], 'up': [800, 800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [],3:[], 'crossed': 0}, 'down': {0: [], 1: [], 2: [],3:[], 'crossed': 0},
            'left': {0: [], 1: [], 2: [],3:[], 'crossed': 0}, 'up': {0: [], 1: [], 2: [],3:[], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

vehiclesTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
vehiclesNotTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
rotationAngle = 3

# Signal tasvirining koordinatalari, taymer va avtomobillar soni
signalCoods = [(480, 640), (490, 190), (880, 190), (880, 640)]
signalTimerCoods = [(490, 672), (500, 225), (890, 225), (890, 672)]

# To'xtash chiziqlari koordinatalari
stopLines = {'right': 455, 'down': 220, 'left': 940, 'up': 710}
defaultStop = {'right': 450, 'down': 210, 'left': 960, 'up': 715}
# stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

# Avtomobillar orasidagi bo'shliq
stoppingGap = 15  # to`xtashda bo'shliq
movingGap = 15  # harakatlanishda bo'shliq

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
	def __init__(self, red, yellow, green):
		self.red = red
		self.yellow = yellow
		self.green = green
		self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
	def __init__(self, lane, vehicleClass, direction_number, direction):
		pygame.sprite.Sprite.__init__(self)
		self.lane = lane
		self.vehicleClass = vehicleClass
		self.speed = speeds[vehicleClass]
		self.direction_number = direction_number
		self.direction = direction
		self.x = x[direction][lane]
		self.y = y[direction][lane]
		self.crossed = 0
		self.turned = 0
		self.rotateAngle = 0
		vehicles[direction][lane].append(self)
		self.index = len(vehicles[direction][lane]) - 1
		path = "images/" + direction + "/" + vehicleClass + ".png"
		self.image = pygame.image.load(path)
		if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):  # agar u to'xtash chizig'ini kesib o'tmaguncha transport vositasining bo'lagida 1 dan ortiq transport vositasi bo'lsa
			if (direction == 'right'):

				self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][self.index - 1].image.get_rect().width - stoppingGap  # to'xtash koordinatasini quyidagicha belgilash: keyingi avtomobilning to'xtash koordinatasi - keyingi transport vositasining kengligi - bo'shliq
			elif (direction == 'left'):
				self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
					self.index - 1].image.get_rect().width + stoppingGap
			elif (direction == 'down'):
				self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
					self.index - 1].image.get_rect().height - stoppingGap
			elif (direction == 'up'):
				self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
					self.index - 1].image.get_rect().height + stoppingGap
		else:
			self.stop = defaultStop[direction]
		
		# Yangi boshlash va to'xtash koordinatalarini o'rnating
		if (direction == 'right'):
			temp = self.image.get_rect().width + stoppingGap
			x[direction][lane] -= temp
		elif (direction == 'left'):
			temp = self.image.get_rect().width + stoppingGap
			x[direction][lane] += temp
		elif (direction == 'down'):
			temp = self.image.get_rect().height + stoppingGap
			y[direction][lane] -= temp
		elif (direction == 'up'):
			temp = self.image.get_rect().height + stoppingGap
			y[direction][lane] += temp
		simulation.add(self)
	
	def render(self, screen):
		screen.blit(self.image, (self.x, self.y))
	
	def move(self):
		if (self.direction == 'right'):
			
			if (self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]):
				  # if the image has crossed stop line now
				self.crossed = 1
			if ((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
					currentGreen == [0, 2] and currentYellow != currentGreen)) and (
					self.index == 0 or self.x + self.image.get_rect().width < (
					vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
				# (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
				self.x += self.speed  # move the vehicle
		elif (self.direction == 'down'):
			if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
				self.crossed = 1
			if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
					currentGreen == [1, 3] and currentYellow != currentGreen)) and (
					self.index == 0 or self.y + self.image.get_rect().height < (
					vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
				self.y += self.speed
		elif (self.direction == 'left'):
			if (self.crossed == 0 and self.x < stopLines[self.direction]):
				self.crossed = 1
			if ((self.x >= self.stop or self.crossed == 1 or (currentGreen == [0, 2] and currentYellow != currentGreen)) and (
					self.index == 0 or self.x > (
					vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
				self.index - 1].image.get_rect().width + movingGap))):
				self.x -= self.speed
		elif (self.direction == 'up'):
			if (self.crossed == 0 and self.y < stopLines[self.direction]):
				self.crossed = 1
			if ((self.y >= self.stop or self.crossed == 1 or (currentGreen == [1, 3] and currentYellow != currentGreen)) and (
					self.index == 0 or self.y > (
					vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
				self.index - 1].image.get_rect().height + movingGap))):
				self.y -= self.speed


# Standart qiymatlar bilan signallarni ishga tushirish
def initialize():
	ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
	signals.append(ts1)
	ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
	signals.append(ts2)
	ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
	signals.append(ts3)
	ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
	signals.append(ts4)
	repeat()


def repeat():
	global currentGreen, currentYellow, nextGreen
	while (signals[currentGreen[0]].green > 0 and signals[currentGreen[1]].green > 0):
		updateValues()
		time.sleep(1)

	if currentYellow == 0:
		currentYellow = []  # set yellow signal off
	else:
		currentYellow = [currentGreen[0],currentGreen[1]]  # set yellow signal on
	# reset stop coordinates of lanes and vehicles
	for i in range(0, 3):
		for vehicle in vehicles[directionNumbers[currentGreen[0]]][i]:
			vehicle.stop = defaultStop[directionNumbers[currentGreen[0]]]
	while (signals[currentGreen[0]].yellow > 0 and signals[currentGreen[1]].yellow > 0):  # while the timer of current yellow signal is not zero
		updateValues()
		time.sleep(1)
	if currentYellow == 0:
		currentYellow = []  # set yellow signal off
	else:
		currentYellow = [currentGreen[0],currentGreen[1]]  # set yellow signal on
	
	# reset all signal times of current signal to default times
	signals[currentGreen[0]].green = defaultGreen[0]
	signals[currentGreen[1]].green = defaultGreen[0]
	signals[currentGreen[0]].yellow = defaultYellow
	signals[currentGreen[1]].yellow = defaultYellow
	signals[currentGreen[0]].red = defaultRed
	signals[currentGreen[1]].red = defaultRed

	currentGreen = nextGreen  # set next signal as green signal
	if currentGreen == [0, 2]:
		nextGreen = [1, 3]
	else:
		nextGreen = [0, 2]  # set next green signal
	signals[nextGreen[0]].red = signals[currentGreen[0]].yellow + signals[
		currentGreen[0]].green  # set the red time of next to next signal as (yellow time + green time) of next signal
	signals[nextGreen[1]].red = signals[currentGreen[1]].yellow + signals[
		currentGreen[1]].green  # set the red time of next to next signal as (yellow time + green time) of next signal
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
	while True:
		vehicle_type = random.randint(0, 3)
		lane_number = random.randint(0, 3)
		temp = random.randint(0, 99)
		direction_number = 0
		dist = [25, 50, 75, 100]
		if temp < dist[0]:
			direction_number = 0
		elif temp < dist[1]:
			direction_number = 1
		elif temp < dist[2]:
			direction_number = 2
		elif (temp < dist[3]):
			direction_number = 3
		Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number] )
		time.sleep(0.1)


class Main:
	thread1 = threading.Thread(name = "initialization", target = initialize, args = ())  # initialization
	thread1.daemon = True
	thread1.start()
	
	# Ranglar
	black = (0, 0, 0)
	white = (255, 255, 255)
	
	# Ekran o'lchami
	screenWidth = 1400
	screenHeight = 800
	screenSize = (screenWidth, screenHeight)
	
	# Fon rasmini o'rnatish, ya'ni kesishish tasviri
	background = pygame.image.load('images/choraxa.png')
	
	screen = pygame.display.set_mode(screenSize)
	pygame.display.set_caption("SIMULATION")
	
	# Signal tasvirlari va shrift yuklanmoqda
	redSignal = pygame.image.load('images/signals/red.png')
	yellowSignal = pygame.image.load('images/signals/yellow.png')
	greenSignal = pygame.image.load('images/signals/green.png')
	font = pygame.font.Font(None, 30)
	
	thread2 = threading.Thread(name = "generateVehicles", target = generateVehicles, args = ())  # Generating vehicles
	thread2.daemon = True
	thread2.start()
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
		
		screen.blit(background, (0, 0))  # simulyatsiyada fonni ko'rsatish
		for i in greenSingals:
			if (i==currentGreen):
				if signals[i[0]].green == 0 and signals[i[1]].green == 0:
					screen.blit(yellowSignal, signalCoods[i[0]])
					screen.blit(yellowSignal, signalCoods[i[1]])
					signals[i[1]].signalText = signals[i[1]].yellow
					signals[i[0]].signalText = signals[i[0]].yellow


					
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
			# if (i[0]==currentGreen or i[1]==currentGreen):
			# 	screen.blit(greenSignal, signalCoods[i[0]])
			# 	screen.blit(greenSignal, signalCoods[i[1]])
			# else:
			# 	screen.blit(greenSignal, signalCoods[i[0]])
			# 	screen.blit(greenSignal, signalCoods[i[1]])

				
		# for i in range(0, noOfSignals):
		# 	if (i == currentGreen):
		# 		if (currentYellow == 1):
		# 			signals[i].signalText = signals[i].yellow
					
		# 			screen.blit(yellowSignal, signalCoods[i])
		# 		else:
		# 			signals[i].signalText = signals[i].green
		# 			screen.blit(greenSignal, signalCoods[i])
		# 	else:
		# 		if (signals[i].red <= 10):
		# 			signals[i].signalText = signals[i].red
		# 		else:
		# 			signals[i].signalText = "-"
		# 		screen.blit(redSignal, signalCoods[i])
		signalTexts = ["", "", "", ""]
		
		# signal taymerini ko'rsatish
		for i in range(0, noOfSignals):
			signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)

			screen.blit(signalTexts[i], signalTimerCoods[i])
		
		# transport vositalarini ko'rsatish
		for vehicle in simulation:
			screen.blit(vehicle.image, [vehicle.x, vehicle.y])
			vehicle.move()
		pygame.display.update()


Main()
