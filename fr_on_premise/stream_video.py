from fr_on_premise.websocket_client import *

import functools
import json
import time
import cv2

class StreamVideo(WebSocketClient):

    def __init__(self):
        self.connect_timeout = DEFAULT_CONNECT_TIMEOUT
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.time_out_stream = None
        

    def _on_message(self, msg):
        print('Reading message')
        print(msg)
        # ores = json.loads(msg)
        # if len(ores) > 0:
        #     self.plot_recognition_info(self.original_frame, ores)
        
        # cv2.putText(self.original_frame, sfps, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), thickness = 2)
        # cv2.imshow("Candiru follows the stream", cv2.resize(self.original_frame, (0,0), fx=0.3, fy=0.3))
        # cv2.waitKey(1)
        self.call_stream()


    def call_stream(self):
        if self.time_out_stream != None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)

        self.stream()
        deadline = time.time() + 1
        self.time_out_stream = ioloop.IOLoop().instance().add_timeout(deadline, self.call_stream)

    
    def config(self, stream_path, ws_url):
        self.video = cv2.VideoCapture(stream_path)
        if self.video.isOpened() == False:
            print('problem opening', stream_path)
            return

        self.connect(ws_url)


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(data, binary=True)


    def _on_connection_success(self):
        self.stream()


    def plot_recognition_info(self, image, ores):
        for rec in ores['people']:
            l = rec['top_left']['x']
            t = rec['top_left']['y']
            r = rec['bottom_right']['x']
            b = rec['bottom_right']['y']
            tl = [l, t]
            br = [r, b]
            cv2.rectangle(image, (int(tl[0]), int(tl[1])), (int(br[0]), int(br[1])), (165, 142, 254), 4)
            
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            label = rec["recognition"]["predictedLabel"]
            
            (text_size, baseline) = cv2.getTextSize(label, font_face, 1, 2);
            text_pt = (int(tl[0]), int(tl[1])-10)
            cv2.rectangle(image, (text_pt[0], text_pt[1]-text_size[1]-4), (text_pt[0] + text_size[0], text_pt[1]+4), (165, 142, 254), -1)
            cv2.putText(image, label, text_pt, font_face, 1, (255, 255, 255), 2)


    @gen.coroutine
    def stream(self):
        print('streaming!!!')
        ret, self.original_frame = self.video.read()

        # what video.read() returns when the video is over? Zero sized image? A None variable?
        if self.original_frame.size < 1000:
            self.close()
            return

        frame = cv2.cvtColor(self.original_frame, cv2.COLOR_BGR2GRAY)
        _, framecomp = cv2.imencode('.jpg', frame)

        self.send(framecomp.tobytes())
