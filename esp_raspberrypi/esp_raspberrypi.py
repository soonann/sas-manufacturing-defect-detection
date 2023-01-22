## The purpose of this script is to send listen for a physical button press on the raspberry pi
## Upon a button press, it will take a picture with the raspberry pi camera and process (crop,resize,encode) 
## the image before sending it to ESP via a shortlived websocket connection for scoring.

## After sending scoring the image, it will attempt to retrieve the results of the scoring via REST api calls
## The results will then be sent to the arduino which controls the robotic arm based on the results of the scoring

# Python 2.7 

import serial # Library for using the USB to transfer data 
import time # Library to make the program wait for a few seconds
from datetime import datetime # Used to generate a unique time key to serve as an ID
import struct # Library to pack the data as bytes for transfer on the USB port
import commands # Library to execute commands on the commandline and get results of command
import requests # Library to execute REST Api calls to ESP 
import base64 # Library to encode data in base64 format, particularly images, for ESP to be able to take in
from picamera import PiCamera # Library to control the raspberry pi camera
import websocket # Library to create a websocket connection
import json # Library to parse json data
import cv2 # Opencv2, a computer vision library used to save/encode/crop/resize images 
from grovepi import * # Library to control the grovepi plugins for the raspberry pi   
from grove_rgb_lcd import * # Library to control the LCD screen for the raspberry pi


# Send message through serial port
def executeAction(action_num):

    print('action =' + str(action_num))
    resp, port = commands.getstatusoutput('dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1') # get the serial port number
    
    ser=serial.Serial('/dev/'+port, 9600) # establish connection through serial port
    
    ser.flushInput() # Flush the inputs & outputs to clear previous buffers
    ser.flushOutput()

    num = action_num # Action number, either 1 or 2 depending on the the scoring results in the

    numByte = struct.pack('b', num) # Convert the integer to bytes for transfering on USB port

    ser.write(numByte) # Send the bytes and close the connection
    ser.close()


# Takes a picture of the object, crops a certain region, resizes the image, and encodes it as base64
def takePicture ():

    ## OPTIONAL (a few parameters that enables you to tweak the raspberrypi camera's resolution and postion) 
    #camera.rotation = 180
    #camera.resolution = (1200,1200)
    #camera.resolution = (64,64)

    camera.start_preview() # Initialise the raspberry pi camera 

    time.sleep(1) # Wait for 1 second 

    imgname = 'img.jpg'
    
    image = camera.capture(sourceFolder+'img.jpg',format='jpeg') # Save image as jpg
    
    camera.stop_preview() # Stop camera

    frame_to_convert = cv2.imread(sourceFolder+'img.jpg') # Read the saved jpg file back in
    
    frame_small = frame_to_convert[y:y+h, x:x+w] # Crop a region of the entire image
    
    frame_small = cv2.resize(frame_small, (224,224)) # Resize cropped image to 224x224
    
    filename = sourceFolder+'img2.jpg'  
    cv2.imwrite(filename , frame_small, [cv2.IMWRITE_JPEG_QUALITY, 95] ) # Save the resized and cropped image


    with open( filename , "rb") as image: # Read the resized and cropped image back in 
        img_str = base64.b64encode(bytes(image.read())).decode("utf-8") # Encode image in base64

    return img_str # Return encoded image

    
# Creates a shortlived websocket connection and sends the image over to ESP
def sendImageByWS(url,csv):

    print('sendImageByWS :' + url)
    
    ws = websocket.create_connection(url) # Create websocket connection
   
    ws.send(csv)  # Send csv formatted data to ESP
    print('sent')
    
    ws.close() # Close websocket connection
    print('ws closed')

                   
# Get the scoring results of the image
def getScore (url,idx):

    # Specify request headers for REST call 
    headers = {'Accept': 'application/json'}
    print(url+idx)
    
    # Make get request to ESP and filter results by unique id 
    req = requests.get(url+idx, headers = headers)

    # Parse request response from ESP 
    result = req.text
    js = json.loads(result)
    print js['events'][1]['event']['I__label_']

    # Get the label of the response
    typeCode = js['events'][1]['event']['I__label_']
    
    # Type 3 result means the item is defective
    if typeCode == 'Type3' :
        setText('Reject')
        actioncode = 1

    # Type 4 result means the item is not defective
    elif typeCode == 'Type4' :
        setText('Accept')
        actioncode = 2

    return actioncode



def loadESPProject(url):
	response = requests.request(method='PUT', url= 'http://' + url +  "/SASESP/projects" + '/RobotArm?overwrite=true&projectUrl='+'file:///opt/sas/projects/robot_arm/RobotArm.xml')
	print response.text




# URL to send websocket connections & REST calls to, at the HTTP port
espServer = "<ip-address>:55580"
espInjectURL = 'ws://' + espServer + '/SASESP/publishers/RobotArm/contQuery/Source_Img'
espResultURL = 'http://' + espServer +'/SASESP/events/RobotArm/contQuery/Copy_Scores?Id='           

loadESPProject(espServer) # Loads and runs the Robot Arm ESP project

sourceFolder = '/tmp/' # Indicate image saving folder for temporary images
imgname = '/home/pi/Desktop/image2.jpg' # Indicate image saving path for processes images, saving a new image will overwrite the old one
img_str = '' # Variable to save the blob/base64 encoded image
action_num = 0 # Variable to store the action code for the robotic arm


# Specify the region to crop from the entire image *used in the takePicture() function*
x = 620
y = 350
h = 570
w = 570


button = 3 # Init button and Camera
pinMode(button,"INPUT")	# Assign mode for Button as input

camera = PiCamera() # Create a picamera object

setRGB(0,255,0) # Initialise LCD screen
setText("ready to go...")  # update the RGB LCD display


# Loop to listen for clicks on the button
while True:
    try:

        button_status= digitalRead(button) #Read the Button status
        if button_status:	#If the Button is in HIGH position, run the program

            setText("Click Button...")  # update the RGB LCD display

            img_str = takePicture() # Take picture

            setText("Picture Taken")  # update the RGB LCD display
           
            idx = str(datetime.now().strftime('%Y%m%d%H%M%S'))  # Generate Unique Key Id for each event
            print (idx)
           
            csv = 'i,n,'+idx+','+ img_str + '\n'   # format data in csv format for sending
                        
            sendImageByWS (espInjectURL, csv) # Send request to ESP server via WebSocket

            setText("Scoring...")  # update the RGB LCD display
            
            time.sleep(2.5) # wait 0.5 sec to get result from ESP server

            action_num = getScore(espResultURL, idx) # Parse and get the scoring results and get action code to control the robot arm
            
            executeAction(action_num) # control the robot arm based on the action code

            #executeAction(0) # Robot arm back to initial position

        else:
            print ("Off") #If Button is in Off position, print "Off" on the screen
            
    except KeyboardInterrupt:   # Stop the buzzer before stopping
        break
    
    except (IOError,TypeError,ValueError) as e:
        print("Error : "+ str(e))

    time.sleep(1)


## Created by: Alex Yang & Tan Soon Ann
## If you have any queries, feel free to contact me at sudo@soonann.dev  