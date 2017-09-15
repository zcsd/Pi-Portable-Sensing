import os
import pygame
from pygame.locals import *
from gpiozero import MCP3008

# Color
GRAY = (144, 144, 144)
WHITE = (255, 255 ,255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Rectbutton
exitButton = (420,0,70,40)
switchButton = (0,0,70,40)

# Draw Basic UI
def drawBasic():
	titleText = pygame.font.Font("freesansbold.ttf",22)
	titleSurf, titleRect = text_objects("Gas Monitor", titleText, BLUE)
	titleRect.center = (240, 25)
	screen.blit(titleSurf, titleRect)
	
	gasText = pygame.font.Font("freesansbold.ttf",22)
	textSurf, textRect = text_objects("Ozone       Smoke       CO         H2,CO", gasText, BLACK)
	textRect.center = (240, 300)
	screen.blit(textSurf, textRect)
	
	pygame.draw.rect(screen, GRAY, exitButton)
	exitText = pygame.font.Font("freesansbold.ttf",20)
	TextSurf, TextRect = text_objects("Exit", exitText, BLACK)
	TextRect.center = (451, 18)
	screen.blit(TextSurf, TextRect)
	
	pygame.draw.rect(screen, GRAY, switchButton)
	switchText = pygame.font.Font("freesansbold.ttf",20)
	swtextSurf, swtextRect = text_objects("IR", switchText, BLACK)
	swtextRect.center = (35, 20)
	screen.blit(swtextSurf, swtextRect)
	
	pygame.draw.rect(screen, GRAY, [64, 69, 52, 212], 1)
	pygame.draw.rect(screen, GRAY, [164, 69, 52, 212], 1)
	pygame.draw.rect(screen, GRAY, [264, 69, 52, 212], 1)
	pygame.draw.rect(screen, GRAY, [364, 69, 52, 212], 1)

# Update Gas Bar
def gasBar():
	global v1, v2, v3, v4

	if pot1.value * 200 > 5:
		valueGas1 = int(pot1.value * 200)
		v1 = valueGas1
	else:
		valueGas1 = v1
		
	if pot2.value * 200 > 5:
		valueGas2 = int(pot2.value * 200)
		v2 = valueGas2
	else:
		valueGas2 = v2
			
	if pot3.value * 200 > 5:
		valueGas3 = int(pot3.value * 200)
		v3 = valueGas3
	else:
		valueGas3 = v3
			
	if pot4.value * 200 > 5:
		valueGas4 = int(pot4.value * 200)
		v4 = valueGas4
	else:
		valueGas4 = v4
		
	gas1Bar = (65, 270-valueGas1, 50, 10+valueGas1)
	gas2Bar = (165, 270-valueGas2, 50, 10+valueGas2)
	gas3Bar = (265, 270-valueGas3, 50, 10+valueGas3)
	gas4Bar = (365, 270-valueGas4, 50, 10+valueGas4)
	color1 = GREEN
	color2 = GREEN
	color3 = GREEN
	color4 = GREEN
	if(valueGas1 > 100):
		color1 = RED
	if(valueGas2 > 100): 
		color2 = RED
	if(valueGas3 > 100): 
		color3 = RED
	if(valueGas4 > 100): 
		color4 = RED
	valueText = ' ' + str(valueGas1/2) + '%          ' + str(valueGas2/2) + '%           ' + str(valueGas3/2) + '%          ' + str(valueGas4/2) + '% '
	barText = pygame.font.Font("freesansbold.ttf",20)
	textSurf, textRect = text_objects(valueText, barText, GRAY)
	textRect.center = (240, 60)
	screen.blit(textSurf, textRect)
		
	pygame.draw.rect(screen, color1, gas1Bar)
	pygame.draw.rect(screen, color2, gas2Bar)
	pygame.draw.rect(screen, color3, gas3Bar)
	pygame.draw.rect(screen, color4, gas4Bar)

# For draw text
def text_objects(text, font, color):
	textSurface = font.render(text, True, color)
	return textSurface, textSurface.get_rect()

# Button selected
def	selected(buttonRect, pos):
	x1 = buttonRect[0]
	y1 = buttonRect[1]
	x2 = x1 + buttonRect[2] - 1
	y2 =  y1 + buttonRect[3] - 1
	if ( (pos[0] >= x1) and (pos[0] <= x2) and (pos[1] >= y1) and pos[1] <= y2 ):
		return True
	else:
		return False	
'''						
# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')
'''
# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
# screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen = pygame.display.set_mode([480, 320])

# Init MQ sensor
pot1 = MCP3008(channel=5, clock_pin=21, mosi_pin=20, miso_pin=12, select_pin=16)
pot2 = MCP3008(channel=4, clock_pin=21, mosi_pin=20, miso_pin=12, select_pin=16)
pot3 = MCP3008(channel=3, clock_pin=21, mosi_pin=20, miso_pin=12, select_pin=16)
pot4 = MCP3008(channel=2, clock_pin=21, mosi_pin=20, miso_pin=12, select_pin=16)
v1 = 1
v2 = 1
v3 = 1
v4 = 1

while(True):
	for event in pygame.event.get():
		if event.type is MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			if selected(exitButton, pos):
				exit()
			elif selected(switchButton, pos):
				pygame.quit()
				execfile("cam.py")
				
	screen.fill(WHITE)	
	drawBasic()
	gasBar()	
	
	pygame.display.update()
					
