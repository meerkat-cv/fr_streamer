
import cv2
from fr_on_premise import websocket_tc
import numpy as np
import time
import json
from tornado import ioloop

def circular_counter(max):
    """helper function that creates an eternal counter till a max value"""
    x = 0
    while True:
        if x == max:
            x = 0
        x += 1
        yield x


 
class CvTimer(object):
    def __init__(self):
        self.tick_frequency = cv2.getTickFrequency()
        self.tick_at_init = cv2.getTickCount()
        self.last_tick = self.tick_at_init
        self.fps_len = 10
        self.l_fps_history = [ 10 for x in range(self.fps_len)]
        self.fps_counter = circular_counter(self.fps_len)

    def reset(self):
        self.last_tick = cv2.getTickCount()

    def get_tick_now(self):
        return cv2.getTickCount()

    @property
    def fps(self):
        fps = self.tick_frequency / (self.get_tick_now() - self.last_tick)
        self.l_fps_history[self.fps_counter.__next__() - 1] = fps
        self.reset()
        return fps

    @property
    def avg_fps(self):
        return sum(self.l_fps_history) / float(self.fps_len)



class TestWebSocketClient(websocket_tc.WebSocketClient):

    def _on_message(self, msg):
        print(msg)
        # deadline = time.time() + 1
        # ioloop.IOLoop().instance().add_timeout(
        #     deadline, functools.partial(self.send, str(int(time.time()))))

    def _on_connection_success(self):
        print('Connected!')
        # self.send(str(int(time.time())))

    def _on_connection_close(self):
        print('Connection closed!')

    def _on_connection_error(self, exception):
        print('Connection error: %s', exception)



class StreamVideo:

    def __init__(self, stream_path, ws_url):
        # cv2.namedWindow("Candiru follows the stream", cv2.WINDOW_NORMAL) 
        self.video = cv2.VideoCapture(0)
        # self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
        # self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);
        # # print("Camera framerate:",self.video.get(cv2.CAP_PROP_FPS))
        # self.video.set(cv2.CAP_PROP_FPS, 60);
        # self.video.set(cv2.CAP_PROP_CONVERT_RGB, False)

        # self.ws = websocket.create_connection(ws_url)
        self.ws = TestWebSocketClient()
        self.ws.connect(ws_url)

        try:
            print('hey')
            my_io_loop = ioloop.IOLoop()
            my_io_loop.make_current()
            my_io_loop.start()
            print('ho')
            time.sleep(10)
        except KeyboardInterrupt:
            self.ws.close()
            self.ws.connect();

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

    def stream(self):
        tick_frequency = cv2.getTickFrequency()
        
        last_tick = cv2.getTickCount()
        fps_history = [ 10 for x in range(30)]
        ifps = 0
        while True:
            ret, self.original_frame = self.video.read()
            frame = cv2.cvtColor(self.original_frame, cv2.COLOR_BGR2GRAY)
            # print(frame.shape)
            # frame = cv2.resize(frame, (480,320))

            _, framecomp = cv2.imencode('.jpg', frame)

            start = time.time()
            # self.ws.send_binary(framecomp)
            self.ws.send(framecomp)
            end = time.time()
            print("Sending binary:", str((end - start)*1000))        
            # result = self.ws.recv()

            # ores = json.loads(result)
            # if len(ores) > 0:
            #     self.plot_recognition_info(self.original_frame, ores)

            fps = tick_frequency/(cv2.getTickCount() - last_tick)
            fps_history[ifps % 30] = fps
            ifps = ifps+1
            last_tick = cv2.getTickCount()
            sfps = "fps: {0:5.2f}".format(sum(fps_history)/30.)
            print(sfps)

            cv2.putText(self.original_frame, sfps, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), thickness = 2)
            cv2.imshow("Candiru follows the stream", cv2.resize(self.original_frame, (0,0), fx=0.3, fy=0.3))
            cv2.waitKey(1)


            
            # exit(1)

            