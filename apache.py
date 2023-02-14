import cv2
import pyrebase
import socket
import subprocess

# Initialize Firebase
firebase_config = {
    # Add your Firebase config here
}
firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()

# Initialize socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8888))
s.listen()

while True:
    conn, addr = s.accept()

    # Receive command from client
    command = conn.recv(1024).decode()

    # Process command
    if command == 'shutdown':
        subprocess.call(['sudo', 'shutdown', '-h', 'now'])
    elif command == 'reboot':
        subprocess.call(['sudo', 'reboot'])
    elif command == 'take_photo':
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        cv2.imwrite('photo.jpg', frame)
        storage.child('photos/photo.jpg').put('photo.jpg')
        camera.release()
    elif command == 'record_video':
        camera = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('video.avi', fourcc, 20.0, (640, 480))

        while True:
            ret, frame = camera.read()
            out.write(frame)
            if cv2.waitKey(1) == ord('q'):
                break

        out.release()
        camera.release()
        storage.child('videos/video.avi').put('video.avi')

    # Send response to client
    conn.send('OK'.encode())

    # Close connection
    conn.close()
