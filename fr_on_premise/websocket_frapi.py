from fr_on_premise.base_websocket_client import *
from fr_on_premise import video_stream
from functools import partial
import json
import time
import cv2
import logging


class WebSocketFrapi(WebSocketClient):

    def __init__(self):
        self.connect_timeout = DEFAULT_CONNECT_TIMEOUT
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.time_out_stream = None
        self.original_frame = None
        self.stream_label = None
        self.closing = False
        self.ws_url = None
        self.video_url = None
        

    def _on_message(self, msg):
        if self.closing == True:
            return
        else:
            ores = json.loads(msg)

            if 'error' in ores:
                logging.error('Problem with server: '+ores['error'])
                self.close()
                self.client.end_transmission(self.stream_label, close_from_socket = True)
            else:
                self.client.on_message(self.original_frame, ores, self.stream_label)
                self.call_stream()


    def call_stream(self):
        if self.time_out_stream is not None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)

        self.stream()
        deadline = time.time() + 10
        self.time_out_stream = ioloop.IOLoop().instance().add_timeout(deadline, self.end_stream)

    
    def config(self, config_data, ws_url, stream_label, client):
        self.ws_url = ws_url
        self.video = video_stream.load_from_config(config_data)
        self.client = client
        self.stream_label = str(stream_label)
        if self.video.isOpened() == False:
            return (False, 'Problem opening '+stream_label)

        self.connect(ws_url)
        
        if config_data.get('video_file') is not None:
            self.video_url = config_data['video_file']
        elif config_data.get('camera_url') is not None:
            self.video_url = config_data['camera_url']
        elif config_data.get('image_dir') is not None:
            self.video_url = config_data['image_dir']
        else:
            self.video_url = ''

        return (True, '')


    def get_video_url(self):
        return self.video_url


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection or self.closing:
            return

        self._ws_connection.write_message(data, binary=True)
        

    def end_stream(self):
        self.close()
        self.client.end_transmission(self.stream_label, close_from_socket = True)


    def close(self):
        """Close connection.
        """

        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        logging.warn('Closing connection of stream '+self.stream_label)
        self.closing = True
        if self.time_out_stream is not None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)

        self.video.close()
        self._ws_connection.close()


    def _on_connection_success(self):
        self.stream()


    def _on_connection_error(self, exception):
        self.video.close()
        self.client.end_transmission(self.stream_label, close_from_socket = True)
        logging.error('Problem connecting to the given websocket: '+self.ws_url)


    @gen.coroutine
    def stream(self):
        self.original_frame = self.video.get_next_frame()

        if self.original_frame is None:
            self.closing = True
            return

        frame = cv2.cvtColor(self.original_frame, cv2.COLOR_BGR2GRAY)
        _, framecomp = cv2.imencode('.jpg', frame)

        # the function to write back on the websocket must be executed on
        # the ioloop thread, which is why i'm using IOLoop.instance()
        res = ioloop.IOLoop.instance().add_callback(partial(self.send, framecomp.tobytes()))
