from fr_on_premise.stream_video import *
from tornado import ioloop
from threading import Thread

class FrapiClient():

    def __init__(self):
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = []
        def ioloop_fun(self):
            try:
                ioloop.IOLoop.instance().start()
            except KeyboardInterrupt:
                self.end_transmissions()

        t = Thread(target = ioloop_fun, args = (self,))
        t.start()


    def transmit(self, video_name, ws_url):
        stream = StreamVideo()
        stream.config(video_name, ws_url)
        self.streams.append(stream)


    def end_transmissions(self):
        for s in self.streams:
            s.close()
        

