from tornado import ioloop
from fr_on_premise.frapi_client import FrapiClient
import time

def main():
    frapi = FrapiClient()
    frapi.transmit('/home/guilherme/obama.mp4', 'ws://localhost:4444/frapi_echo?api_key=f0848b0439c00687dbf18296623b9754')
    frapi.transmit('/home/guilherme/obama.mp4', 'ws://localhost:4444/frapi_echo?api_key=f0848b0439c00687dbf18296623b9754')
    frapi.transmit('/home/guilherme/obama.mp4', 'ws://localhost:4444/frapi_echo?api_key=f0848b0439c00687dbf18296623b9754')

    try:
    	time.sleep(100)
    except KeyboardInterrupt:
        frapi.end_transmissions()
    

if __name__ == '__main__':
    main()
