from fr_on_premise.stream_video import *
from tornado import ioloop
from threading import Thread

class FrapiClient():

    def __init__(self):
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = []
        self.window_name = []
        def ioloop_fun(self):
            try:
                ioloop.IOLoop.instance().start()
            except KeyboardInterrupt:
                self.end_transmissions()

        t = Thread(target = ioloop_fun, args = (self,))
        t.start()


    def transmit(self, window_name, video_name, ws_url):
        self.window_name.append(window_name)
        stream_id = len(self.window_name)-1
        stream = StreamVideo()
        stream.config(video_name, ws_url, stream_id, self)
        self.streams.append(stream)



    def on_message(self, image, ores, stream_id):
        if image is not None and 'people' in ores:
            self.plot_recognition_info(image, ores, stream_id)


    def plot_recognition_info(self, image, ores, stream_id):
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


        cv2.imshow(self.window_name[stream_id], image)
        cv2.waitKey(1)
        


    def end_transmissions(self):
        for s in self.streams:
            s.close()
        

