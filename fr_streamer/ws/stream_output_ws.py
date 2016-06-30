import base64
import tornado
import numpy as np
import cv2
import tornado.websocket 
import tornado.speedups
import json
import time
import cv2
import logging
from threading import Lock
from fr_on_premise.frapi_client import FrapiClient
from fr_on_premise import app

class StreamOutputWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request,
                                                                      **kwargs)
        self.mtx = Lock()
        self.is_open = False
        self.stream_label = 'None'
        self.frapi_client = FrapiClient.instance()
        

    def check_origin(self, origin):
        return True


    def open(self):
        app.logger.info('opening StreamOutputWebSocket '+self.stream_label)
        self.is_open = True
        self.stream_label = self.get_argument('stream_label')
        self.frapi_client.add_stream_output_ws(self, self.stream_label)


    def send_msg(self, recog_result, frame):
        # enforce serial connection
        if self.is_open == False:
            return

        self.mtx.acquire()
        try:
            _, framecomp = cv2.imencode('.jpg', frame)
            self.write_message(base64.b64encode(framecomp), binary=False)
        except:
            app.logger.error('Problem sending frame from websocket ' + self.stream_label )

        self.mtx.release()


    def on_message(self, message):
        pass

        
    def on_close(self):
        app.logger.info('Closing StreamOutputWebSocket - '+ self.stream_label)
        self.is_open = False
        self.frapi_client.remove_stream_output_ws(self.stream_label)
