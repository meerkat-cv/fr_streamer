from tornado import ioloop
from fr_on_premise.frapi_client import FrapiClient
from fr_on_premise.video_stream import VideoStream
import time
import cv2

def main():
    # frapi = FrapiClient()
    # frapi.transmit('Fickel', 'config.json', 'ws://localhost:4444/recognize?api_key=35cac5b9593ff5ebc71b311d4ecf8b42')
    # # frapi.transmit('Obama', 'config_obama.json', 'ws://localhost:4444/recognize?api_key=35cac5b9593ff5ebc71b311d4ecf8b42')
    
    # try:
    #   time.sleep(100)
    # except KeyboardInterrupt:
    #     frapi.end_transmissions()

    stream = VideoStream()
    video = stream.read_video_stream('config.json')

    try:
        while True:
            frame = video.get_next_frame()
            if frame is None:
                video.close()
                break
            cv2.imshow('test', frame)
            cv2.waitKey(1)
            
    except KeyboardInterrupt:
        video.close()

    

if __name__ == '__main__':
    main()
