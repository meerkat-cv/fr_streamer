from tornado import ioloop
from fr_on_premise.frapi_client import FrapiClient
import time

def main():
    frapi = FrapiClient()
    frapi.transmit('Fickel', '/home/guilherme/meerkat/datasets/meerkat_friends/guilherme_training.avi', 'ws://localhost:4444/recognize?api_key=15220085839d05fdc0bb28bd0f90732e')
    frapi.transmit('Obama', '/home/guilherme/obama.mp4', 'ws://localhost:4444/recognize?api_key=15220085839d05fdc0bb28bd0f90732e')
    
    try:
    	time.sleep(100)
    except KeyboardInterrupt:
        frapi.end_transmissions()
    

if __name__ == '__main__':
    main()
