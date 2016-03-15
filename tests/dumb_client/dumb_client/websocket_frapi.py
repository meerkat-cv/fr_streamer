from dumb_client.base_websocket_client import *
from functools import partial
import json
import time
import cv2
import logging
import numpy as np

def read_cvimage_from_bytes(stream):
    try:
        arr = np.asarray(bytearray(stream), dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        height, width = image.shape[:2]
        if height <= 0 or width <= 0:
            raise Exception('Invalid image file from stream')
    except:
        raise Exception('Invalid image file from stream')

    return image


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
            if isinstance(msg, str):
                print('on message', msg)
            elif isinstance(msg, bytes):
                im = read_cvimage_from_bytes(msg)
                cv2.imshow("Frame", im)
                cv2.waitKey(1)
                print('on message binary')
            else:
                print('Bad message type: ', type(msg))


    
    def close(self):
        """Close connection.
        """

        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        logging.warn('Closing connection of stream ')
        self.closing = True
        if self.time_out_stream is not None:
            ioloop.IOLoop().instance().remove_timeout(self.time_out_stream)

        self._ws_connection.close()


    def _on_connection_success(self):
        print('_on_connection_success')


    def _on_connection_error(self, exception):
        logging.error('Problem connecting to the given websocket: ')
