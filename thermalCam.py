import numpy as np
import cv2
import os
import time
import sys
import fnmatch
import pygame
import imutils
import usb.core
import usb.util
from pygame.locals import *
from PIL import Image, ImageTk
from numpy import array
from scipy.misc import toimage
from scipy import ndimage
from scipy import misc
import colorscale # colorscale.py

# Color Definition
GRAY = (188, 188, 188)
WHITE = (255, 255 ,255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Rectbutton
colorButton = (420,0,70,40)
switchButton = (0,0,70,40)
captureButton = (0, 80, 480, 240)

im2arrF = None	
fps_t = 0
fps_f = 0
isColor = False
maxTemp = 0
isCapture = 0
isShowText = False
showCount = 999

# Draw Basic UI
def drawBasic():
    global isShowText, showCount
 
    if isColor:
        #pygame.draw.rect(screen, GRAY, colorButton)
        exitText = pygame.font.Font("freesansbold.ttf",20)            
        TextSurf, TextRect = text_objects("Gray", exitText, BLUE)
    else:
        #pygame.draw.rect(screen, GRAY, colorButton)
        exitText = pygame.font.Font("freesansbold.ttf",20)
        TextSurf, TextRect = text_objects("Color", exitText, BLUE)
    TextRect.center = (451, 18)
    screen.blit(TextSurf, TextRect)

    if isShowText:
        showCount = 0
        isShowText = 0
    
    if showCount < 10:
        showCount = showCount + 1
        showText = pygame.font.Font("freesansbold.ttf",20)            
        showTextSurf, showTextRect = text_objects("Image Saved", showText, RED)
        showTextRect.center = (240, 160)
        screen.blit(showTextSurf, showTextRect)
    else:
        isShowText = 0
    
    #pygame.draw.rect(screen, GRAY, switchButton)
    switchText = pygame.font.Font("freesansbold.ttf",20)
    swtextSurf, swtextRect = text_objects("IR", switchText, BLUE)
    swtextRect.center = (35, 20)
    screen.blit(swtextSurf, swtextRect)
    
    tempText = pygame.font.Font("freesansbold.ttf",20)
    temptextSurf, temptextRect = text_objects(str(round(maxTemp,1)), tempText, RED)
    temptextRect.center = (275, 20)
    screen.blit(temptextSurf, temptextRect)
	
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

# Get display frame of WebCam
def getDisplayWCam():
    ret, frame = cap.read()
    rotated = imutils.rotate(frame, 180)
    display = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)

    return display

# Get display frame of Seek Thermal, gray or color
def getDisplaySeek():
    frameSeek = getSeekRaw()

    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frameSeek)
    #print maxVal
    #print frameSeek[208/2, 156/2]

    if not isColor:
		# Grayscale thermal image
        imgTemp = toimage(frameSeek)
        imgTemp.save("tmp.jpg")
        toZoomSeek = cv2.imread("tmp.jpg")
        #cv2.circle(toZoomSeek,(70, 52),5,(255,0,0),-1)
        #cv2.circle(toZoomSeek,(140, 104),5,(255,0,0),-1)
        cv2.rectangle(toZoomSeek, (50,30),(160,120),(0,255,0),1)
        display = cv2.resize(toZoomSeek,(320,240))
    else:
		# Color Thermal image
        tempSeek = frameSeek
        tempSeek.clip(20, 1024, out=tempSeek)
        tempSeek -= 20
        tempSeek //= (1024 - 20 + 1) / 256
        tempSeek = tempSeek.astype("uint8")
        # may select different color palette from colorscale.py
        conv = colorscale.GrayToRGB(colorscale.GreenRedPalette())
        cred = np.frompyfunc(conv.get_red, 1, 1)
        cgreen = np.frompyfunc(conv.get_green, 1, 1)
        cblue = np.frompyfunc(conv.get_blue, 1, 1)
        colorSeek = np.dstack((cred(tempSeek).astype(tempSeek.dtype), cgreen(tempSeek).astype(tempSeek.dtype), cblue(tempSeek).astype(tempSeek.dtype)))
        cv2.rectangle(colorSeek, (50,30),(160,120),(0,0,0),1)
        display = cv2.resize(colorSeek,(320,240))
        
    return display
				
# Seek send msg
def send_msg(bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
    assert (dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))

# Deinit the Seek 
def deinit():
    msg = '\x00\x00'
    for i in range(3):
        send_msg(0x41, 0x3C, 0, 0, msg)

# A lot of setup for seek
def setupSeek():
    receive_msg = dev.ctrl_transfer
    
    reattach = False
    if dev.is_kernel_driver_active(0):
		reattach = True
		dev.detach_kernel_driver(0)
    # set the active configuration. With no arguments, the first configuration will be the active one
    dev.set_configuration()
    
    # get an endpoint instance
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    ep = usb.util.find_descriptor(intf, custom_match=custom_match)   # match the first OUT endpoint
    assert ep is not None
   
    # Setup device
    try:
        msg = '\x01'
        send_msg(0x41, 0x54, 0, 0, msg)
    except Exception as e:
        deinit()
        msg = '\x01'
        send_msg(0x41, 0x54, 0, 0, msg)

    send_msg(0x41, 0x3C, 0, 0, '\x00\x00')
    ret1 = receive_msg(0xC1, 0x4E, 0, 0, 4)
    ret2 = receive_msg(0xC1, 0x36, 0, 0, 12)
    send_msg(0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')
    ret3 = receive_msg(0xC1, 0x58, 0, 0, 0x40)
    send_msg(0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')
    ret4 = receive_msg(0xC1, 0x58, 0, 0, 0x40)
    send_msg(0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')
    ret5 = receive_msg(0xC1, 0x58, 0, 0, 0x18)
    send_msg(0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')
    ret6 = receive_msg(0xC1, 0x58, 0, 0, 0x0C)
    send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
    ret7 = receive_msg(0xC1, 0x3D, 0, 0, 2)
    send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
    send_msg(0x41, 0x3C, 0, 0, '\x01\x00')
    ret8 = receive_msg(0xC1, 0x3D, 0, 0, 2)

#get max temp(70,52),(140,104)
def getmaxTemp(tempImg):
	#print tempImg.shape
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(tempImg[50:160, 30:120])
	#avg = cv2.mean(tempImg[70:140, 52:104])
	#print avg[0]
	# 210 23 ,
	return ((maxVal+360) / 28)
	
# Get raw data of Seek        
def getSeekRaw():
    global im2arrF
    global maxTemp
    while True:
        # Send read frame request
        send_msg(0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')

        try:
            ret9  = dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
        except usb.USBError as e:
            sys.exit()

        #  1 is a Normal frame, 3 is a Calibration frame
        #  6 may be a pre-calibration frame
        status = ret9[20]
		
        if status == 1:
            #  Convert the raw calibration data to a string array
            calimg = Image.fromstring("I", (208,156), ret9, "raw", "I;16")
            #  Convert the string array to an unsigned numpy int16 array
            im2arr = np.asarray(calimg)
            #print im2arr[104,78]
            im2arrF = im2arr.astype('uint16')

        if status == 3:
            #  Convert the raw calibration data to a string array
            img = Image.fromstring("I", (208,156), ret9, "raw", "I;16")
            #  Convert the string array to an unsigned numpy int16 array
            im1arr = np.asarray(img)
            #a = im1arr[104,78]+im1arr[103,78]+im1arr[105,78]+im1arr[104,77]+im1arr[104,79]
            #print a/4
            im1arrF = im1arr.astype('uint16')
            #  Subtract the calibration array from the image array and add an offset
            additionF = (im1arrF-im2arrF) + 800
            #a = additionF[104,78]+additionF[103,78]+additionF[105,78]+additionF[104,77]+additionF[104,79]
            #print a/5
            #  convert to an image and display with imagemagick
            
            noiselessF = ndimage.median_filter(additionF,3)
            maxTemp = getmaxTemp(noiselessF)
            #print '\rMaxTemp: %.1f' % maxTemp,
            #sys.stdout.flush()
            #print maxTemp
            return noiselessF

# Find max image no.
def imgRange(path):
	global saveIdx
	min = 9999
	max = 0
	try:
	  for file in os.listdir(path):
	    if fnmatch.fnmatch(file, 'IMG_[0-9][0-9][0-9][0-9].jpg'):
	      i = int(file[4:8])
	      saveIdx = i
	      if(i < min): min = i
	      if(i > max): max = i
	finally:
	  return None if min > max else (min, max)

# Save image	
def saveImage(image):
	global loadIdx, saveIdx, isShowText
	
	# scan for the max image index, start at next pos.
	r = imgRange("/home/pi/Thermal-IMG")
	if r is None:
	   saveIdx = 1
	else:
	   saveIdx = r[1] + 1
	   if saveIdx > 9999: saveIdx = 0

	# Scan for next available image slot
	while True:
	  filename = '/home/pi/Thermal-IMG' + '/IMG_' + '%04d' % saveIdx + '.jpg'
	  if not os.path.isfile(filename): break
	  saveIdx += 1
	  if saveIdx > 9999: saveIdx = 0

	cv2.imwrite(filename, image)
	isShowText = 1
	loadIdx = saveIdx
	
# Init Seek Thermal device 0x289d:0x0010
dev = usb.core.find(idVendor=0x289d, idProduct=0X0010)
if not dev:
	print "Seek Thermal Device Not Found"
setupSeek()	

# Init USB camera using opencv	
cap = cv2.VideoCapture(0)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode([480, 320])

imgRange('/home/pi/Thermal-IMG')

while(True):
    # Show Seek Thermal frame
    displaySeek = getDisplaySeek()    
    pyframeSeek = pygame.surfarray.make_surface(displaySeek)
    screen.blit(pyframeSeek, (240, 3))
    
    # Show webcam frame
    displayWCam = getDisplayWCam()
    pyframeWCam = pygame.surfarray.make_surface(displayWCam)
    screen.blit(pyframeWCam, (0, 0))
    
    # cal FPS
    '''
    now = int(time.time())
    fps_f += 1
    if fps_t == 0:
        fps_t = now
    elif fps_t < now:
        print '\rFPS: %.2f' % (1.0 * fps_f / (now-fps_t)),
        sys.stdout.flush()
        fps_t = now
        fps_f = 0
    '''    
    # handle touchscreen event
    for event in pygame.event.get():
        if event.type is MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if selected(colorButton, pos):
                if isColor==True:
				    isColor=False
                elif isColor==False:
                    isColor=True	
                #cap.release()	
                #exit()
            if selected(captureButton, pos):
				tmpImage = cv2.cvtColor(displaySeek, cv2.COLOR_BGR2RGB)
				tmpImage1 = cv2.cvtColor(displayWCam, cv2.COLOR_BGR2RGB)
				savedImg = np.concatenate((tmpImage1, tmpImage),axis = 0)
				saveImage(savedImg)
            elif selected(switchButton, pos):
                usb.util.dispose_resources(dev)
                cap.release()
                pygame.quit()
                execfile("/home/pi/work/cam.py")		
                
    drawBasic()			
    pygame.display.update()
