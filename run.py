from tornado import ioloop
from fr_on_premise.frapi_client import FrapiClient
from fr_on_premise.video_stream import VideoStream
import time
import cv2
from threading import Thread

def main():
    frapi = FrapiClient('config/config.json')

    def t_fun():
        try:
            time.sleep(1)
            start = time.time()
            obama_closed = False
            while True:
                time.sleep(0.1)

                if time.time()-start > 5 and obama_closed == False:
                    print('Ending transmission of Obama')
                    frapi.end_transmission('Obama')
                    obama_closed = True


        except KeyboardInterrupt:
            frapi.end_transmissions()

    t = Thread(target=t_fun)
    t.start()

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        self.end_transmissions()



    

if __name__ == '__main__':
    main()
