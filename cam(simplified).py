import atexit
import cPickle as pickle
import errno
import fnmatch
import io
import os
import os.path
import picamera
import picamera.array
import pygame
from pygame.locals import *
import numpy as np
import stat
import threading
import time
from PIL import Image 

# Color
GRAY = (144, 144, 144)
FONT_COLOR = (200, 200, 200)

# Button Rect
playButton = (30,260,180,60)
exitButton = (270,260,180,60)
takeButton = (0,0,480,250)

# For draw text
def text_objects(text, font):
	textSurface = font.render(text, True, FONT_COLOR)
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
			
# Find max image no.
def imgRange(path):
	global saveIdx
	min = 9999
	max = 0
	try:
	  for file in os.listdir(path):
	    if fnmatch.fnmatch(file, 'IMG_[0-9][0-9][0-9][0-9].JPG'):
	      i = int(file[4:8])
	      saveIdx = i
	      if(i < min): min = i
	      if(i > max): max = i
	finally:
	  return None if min > max else (min, max)

# Take a picture	
def takePicture(frame):
	global loadIdx, saveIdx
	
	# scan for the max image index, start at next pos.
	r = imgRange("/home/pi/Photos")
	if r is None:
	   saveIdx = 1
	else:
	   saveIdx = r[1] + 1
	   if saveIdx > 9999: saveIdx = 0

	# Scan for next available image slot
	while True:
	  filename = '/home/pi/Photos' + '/IMG_' + '%04d' % saveIdx + '.JPG'
	  if not os.path.isfile(filename): break
	  saveIdx += 1
	  if saveIdx > 9999: saveIdx = 0

	img = Image.fromarray(frame)
	img.save(filename)
	loadIdx = saveIdx
						
# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# Init camera and set up default values
camera  = picamera.PiCamera()
atexit.register(camera.close)
camera.resolution = (480,320)
camera.vflip = True
camera.hflip = False

# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
video = picamera.array.PiRGBArray(camera)

imgRange('/home/pi/Photos')

try:
	for frameBuf in camera.capture_continuous(video, format="rgb", use_video_port=True):
		frame = np.rot90(frameBuf.array)
		video.truncate(0)
		pyframe = pygame.surfarray.make_surface(frame)
		screen.fill([0,0,0])
		screen.blit(pyframe, (0,0))
		
		for event in pygame.event.get():
			if event.type is MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				if selected(playButton, pos):
					print "Play"
				elif selected(exitButton, pos):
					pygame.quit()
				elif selected(takeButton, pos):
					takePicture(frame)					
				
		pygame.draw.rect(screen, GRAY, playButton)
		pygame.draw.rect(screen, GRAY, exitButton)
		playText = pygame.font.Font("freesansbold.ttf",50)
		textSurf, textRect = text_objects("Play", playText)
		textRect.center = ((30+90), (260+30))
		screen.blit(textSurf, textRect)
		exitText = pygame.font.Font("freesansbold.ttf",50)
		TextSurf, TextRect = text_objects("Exit", exitText)
		TextRect.center = ((270+90), (260+30))
		screen.blit(TextSurf, TextRect)
		doneText = pygame.font.Font("freesansbold.ttf",20)
		doneSurf, doneRect = text_objects(str(saveIdx), doneText)
		doneRect.center = ((450), (30))
		screen.blit(doneSurf, doneRect)
		
		pygame.display.update()
		

except KeyboardInterrupt, SystemExit:
	pygame.quit()				
