import tornado
import numpy as np
import cv2
import tornado.websocket 
import tornado.speedups
import json
import time
import cv2
from threading import Lock

class StreamOutputWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request,
                                                                      **kwargs)
        self.mtx = Lock()
        self.is_open = False
        

    def check_origin(self, origin):
        return True


    def open(self):
        print('open')
        self.is_open = True


    def send_msg(self, recog_result, frame):
        self.mtx.acquire()
        try:
            self.write_message(json.dumps(recog_result))
            _, framecomp = cv2.imencode('.jpg', frame)
            self.write_message(framecomp.tobytes(), binary=True)
        except:
            print('Problem sending frame from websocket')

        self.mtx.release()


    def on_message(self, message):
        print('on_message')

        
    def on_close(self):
        print('on_close')
        self.is_open = False
