from dumb_client.websocket_frapi import WebSocketFrapi
from threading import Thread
import time

class MainClient():
    def __init__(self):
        print('MainClient init')

    def run(self):
        def run_thread(self):
            time.sleep(1)
            self.ws_stream = WebSocketFrapi()
            ws_url = 'ws://localhost:4443/stream_output'
            self.ws_stream.connect(ws_url)

        t = Thread(target = run_thread, args=(self,))
        t.daemon = True
        t.start()