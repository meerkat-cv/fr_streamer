from flask import Flask
from flask_sockets import Sockets
import numpy as np
import cv2

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        arr = np.asarray(bytearray(message), dtype=np.uint8)
        arr = np.reshape(arr, (256,256))
        print(arr)
        image = arr
        #cv2.imdecode(arr, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        height, width = image.shape[:2]
        print(height)
        print(width)
        cv2.imwrite('received.jpg', image)

        # cv2.waitKey()
        print('written.')
        ws.send("I received this")

@app.route('/')
def hello():
    return 'Hello World!'


#app.run()