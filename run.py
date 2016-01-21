from tornado import ioloop
from fr_on_premise.stream_video import StreamVideo

def main():
    stream = StreamVideo()
    stream.config('/home/guilherme/obama.mp4', 'ws://localhost:4444/frapi_echo?api_key=f0848b0439c00687dbf18296623b9754')

    try:
    	ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        stream.close()
    

if __name__ == '__main__':
    main()
