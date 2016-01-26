from tornado import ioloop
from fr_on_premise.frapi_client import FrapiClient
from fr_on_premise.video_stream import VideoStream
import time
import cv2

def main():
    frapi = FrapiClient('config/config.json')

    try:
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        frapi.end_transmissions()

    

if __name__ == '__main__':
    main()
