import tornado
import numpy as np
import cv2
import tornado.websocket 
import tornado.speedups
import json
import time
import cv2
from threading import Lock
from fr_on_premise.frapi_client import FrapiClient

class StreamOutputWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request,
                                                                      **kwargs)
        self.mtx = Lock()
        self.is_open = False
        self.frapi_client = FrapiClient.instance()
        

    def check_origin(self, origin):
        return True


    def open(self):
        print('open')
        self.is_open = True
        self.frapi_client.add_stream_output_ws(self)


    def send_msg(self, recog_result, frame):
        # enforce serial connection
        if self.is_open == False:
            return

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
        self.frapi_client.remove_stream_output_ws(self)
