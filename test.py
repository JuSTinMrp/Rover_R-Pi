from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from time import sleep
import os
import firebase_admin
from firebase_admin import credentials, storage
from picamera import PiCamera
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Initialize the Firebase app
cred = credentials.Certificate('path/to/firebase/credentials.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-bucket-name.appspot.com'
})
bucket = storage.bucket()

# Set up the GPIO pins for the DC motors
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set the pins for the left motor
lmotorf = 5
lmotorb = 6
GPIO.setup(lmotorf, GPIO.OUT)
GPIO.setup(lmotorb, GPIO.OUT)

# Set the pins for the right motor
rmotorf = 23
rmotorb = 24
GPIO.setup(rmotorf, GPIO.OUT)
GPIO.setup(rmotorb, GPIO.OUT)

# Initialize the Pi camera
camera = PiCamera()
camera.rotation = 180

# Set up the web interface
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photo')
def take_photo():
    # Take a photo and save it to the Pi
    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S") + '.jpg'
    ####################################################
    camera.capture('/home/kali/camera/' + filename)

    # Upload the photo to Firebase
    blob = bucket.blob('photos/' + filename)
    blob.upload_from_filename('/home/kali/camera/' + filename)

    # Delete the photo from the Pi
    os.remove('/home/kali/camera/' + filename)

    return render_template('index.html')

@app.route('/video')
def record_video():
    # Start recording a video and save it to the Pi
    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S") + '.mp4'   #.h264
    camera.start_recording('/home/pi/camera/' + filename)

    # Wait for the user to stop the recording
    sleep(10)  #

    # Stop recording the video
    camera.stop_recording()

    # Convert the video to MP4 format and save it to the Pi
    mp4filename = now.strftime("%Y%m%d_%H%M%S") + '.mp4'
    os.system('MP4Box -add /home/pi/camera/' + filename + ' /home/pi/camera/' + mp4filename)

    # Upload the video to Firebase
    blob = bucket.blob('videos/' + mp4filename)
    blob.upload_from_filename('/home/pi/camera/' + mp4filename)

    # Delete the videos from the Pi
    os.remove('/home/pi/camera/' + filename)
    os.remove('/home/pi/camera/' + mp4filename)

    return render_template('index.html')

@app.route('/motor/<direction>')
def move_motor(direction):
    # Move the motors in the specified direction
    if direction == 'forward':
        print("Moving forward...")
        GPIO.output(lmotorf, GPIO.HIGH)
        GPIO.output(lmotorb, GPIO.HIGH)
        GPIO.output(rmotorf, GPIO.HIGH)
        GPIO.output(rmotorb, GPIO.HIGH)
    elif direction == 'backward':
        print("Moving backward...")
        GPIO.output(lmotorf, GPIO.LOW)
        GPIO.output(lmotorb, GPIO.LOW)
        GPIO.output(rmotorf, GPIO.LOW)
        GPIO.output(rmotorb, GPIO.LOW)
    elif direction == 'left':
        print("Moving left...")
        GPIO.output(lmotorf, GPIO.LOW)
        GPIO.output(lmotorb, GPIO.LOW)
        GPIO.output(rmotorf, GPIO.HIGH)
        GPIO.output(rmotorb, GPIO.HIGH)
    elif direction == 'right':
        print("Moving right...")
        GPIO.output(lmotorf, GPIO.HIGH)
        GPIO.output(lmotorb, GPIO.HIGH)
        GPIO.output(rmotorf, GPIO.LOW)
        GPIO.output(rmotorb, GPIO.LOW)
