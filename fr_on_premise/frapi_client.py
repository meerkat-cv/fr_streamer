from fr_on_premise import websocket_frapi
from tornado import ioloop
from threading import Thread, Lock
from fr_on_premise.temp_coherence import TempCoherence, CoherenceMethod
from fr_on_premise.config import Config
import json
import cv2
import time
import requests, logging
from io import StringIO
from requests_toolbelt import MultipartEncoder

import traceback
import sys

class Singleton(object):
    __singleton_lock = Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class FrapiClient(Singleton):

    def __init__(self):
        self.mtx = Lock()
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = {}
        self.stream_plot = {}
        self.stream_sliding_window = {}
        self.stream_temp_coherence = {}
        self.stream_results_batch = {}
        self.num_streams = 0
        self.config = Config()
        self.out_stream_ws = {}

        try:
            with open('./config/config.json') as data:
                config_data = json.loads(data.read())
            data.close()
            self.update_config(config_data)
        except:
            logging.error('Problem opening default configuration: config/config.json')


    def update_config(self, config_data):
        self.mtx.acquire()
        streams_url = []
        streams_label = []
        for s in list(self.streams.keys()):
            streams_url.append(self.streams[s].get_video_url())
            streams_label.append(s)

        (ok, error, new_transmissions, ended_transmissions) = self.config.update_config(config_data, streams_label, streams_url)
        if not ok:
            self.mtx.release()
            return (ok, error)

        for transmission in ended_transmissions:
            self.end_transmission(transmission, close_from_socket = False)

        for transmission in new_transmissions:
            (ok, error) = self.transmit(transmission)
            if not ok:
                logging.error(error)

        self.mtx.release()
        return (True, None)


    def transmit(self, config_data):
        (ok, error, label) = self.get_stream_label(config_data)
        if not ok:
            return (ok, error)

        self.stream_results_batch[label] = []
        self.stream_plot[label] = config_data.get('plotStream', False)

        if config_data.get('tempCoherence') is not None:
            self.stream_sliding_window[label] = config_data['tempCoherence'].get('tempWindow', 15)
            method = None
            threshold = config_data['tempCoherence'].get('threshold', self.config.min_confidence)
            method_name = config_data['tempCoherence'].get('method', 'hardThreshold')

            if method_name == 'hardThreshold':
                method = CoherenceMethod.hard_threshold
            elif method_name == 'scoreMean':
                method = CoherenceMethod.score_mean
            else:
                method = CoherenceMethod.score_median

            self.stream_temp_coherence[label] = TempCoherence(self.stream_sliding_window[label], method, threshold, label)
            

        self.num_streams = self.num_streams + 1
        ws_stream = websocket_frapi.WebSocketFrapi()
        ws_url = 'ws://' + self.config.ip + ':' + self.config.port + '/recognize?api_key=' + self.config.api_key
        (ok, error) = ws_stream.config(config_data, ws_url, label, self)
        
        if not ok:
            self.streams[label] = None
            self.end_transmission(label, close_from_socket = False)
        else:
            self.streams[label] = ws_stream

        return (ok, error)


    def on_message(self, image, ores, stream_label):
        if stream_label not in list(self.streams.keys()):
            logging.error('Stream '+stream_label+' already closed.')
            return
        
        if image is not None and 'people' in ores and stream_label in self.stream_results_batch:
            post_image = self.config.http_post_config is not None and len(ores['people']) > 0

            if self.stream_sliding_window.get(stream_label) is not None and (self.config.save_json_config is not None or post_image):
                ores = self.stream_temp_coherence[stream_label].add_frame(ores)
            else:
                ores['stream_label'] = stream_label

            if post_image or self.stream_plot[stream_label]:
                debug_image = self.plot_recognition_info(image, ores, stream_label)

            # the output is only activate if there is someone recognized.
            if self.config.save_json_config is not None:
                self.stream_results_batch[stream_label].append(ores)
                if len(self.stream_results_batch[stream_label]) >= self.config.save_json_config['node_frames']:
                    self.save_json_results(stream_label)

            if post_image and len(ores['people']) > 0:
                self.post_result(ores, debug_image)

            # send the results to all the output websockets
            if stream_label in self.out_stream_ws:
                if post_image or self.stream_plot[stream_label]:
                    self.out_stream_ws[stream_label].send_msg(ores, debug_image)
                else:
                    self.out_stream_ws[stream_label].send_msg(ores, image)


    def post_result(self, result, debug_image):
        """
        This function posts the result that is passed to the configured
        function. If no image is required it is a application/json payload,
        otherwise is a multiform/data.
        """
        try:
            if not self.config.http_post_config['post_image']:
                requests.post(self.config.http_post_config['url'], data=json.dumps(result), headers={'Content-type': 'application/json'})
            else:
                cv2.imwrite('debug_image.jpg', debug_image)
                m = MultipartEncoder(fields={'image': ('filename', open('debug_image.jpg', 'rb')), 
                                         'recognition': json.dumps(result)})
                res = requests.post(self.config.http_post_config['url'], data=m, 
                        headers={'Content-Type': m.content_type})
        except:
            logging.warn('Post result to url '+self.config.http_post_config['url']+' failed!');
        

    def save_json_results(self, stream_label):
        file_name = stream_label+'_'+str(time.time())+'.json'
        if stream_label not in list(self.streams.keys()):
            logging.error('Stream '+stream_label+' already closed.')
            return
        with open(self.config.save_json_config['dir']+'/'+file_name, 'w') as fp:
            json.dump(self.stream_results_batch[stream_label], fp, indent=4, separators=(',', ': '))

        self.stream_results_batch[stream_label].clear()


    def plot_recognition_info(self, image, ores, stream_label):
        for idx, rec in enumerate(ores['people']):
            tl = []
            br = []
            if rec.get('top_left') is not None:
                l = rec['top_left']['x']
                t = rec['top_left']['y']
                r = rec['bottom_right']['x']
                b = rec['bottom_right']['y']
                tl = [l, t]
                br = [r, b]
                cv2.rectangle(image, (int(tl[0]), int(tl[1])), (int(br[0]), int(br[1])), (165, 142, 254), 4)
            else:
                tl = [10, 40+idx*40]
            
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            label = rec["recognition"]["predictedLabel"]
            
            (text_size, baseline) = cv2.getTextSize(label, font_face, 1, 2);
            text_pt = (int(tl[0]), int(tl[1])-10)
            cv2.rectangle(image, (text_pt[0], text_pt[1]-text_size[1]-4), (text_pt[0] + text_size[0], text_pt[1]+4), (165, 142, 254), -1)
            cv2.putText(image, label, text_pt, font_face, 1, (255, 255, 255), 2)

        if self.stream_plot[stream_label]:
            cv2.imshow(stream_label, image)
            cv2.waitKey(1)

        return image


    def get_stream_label(self, config_data):
        label = str(config_data['label'])

        if label is None:
            return (False, 'Label not defined', '')
        if label in self.streams:
            return (False, 'Label already defined', '')

        return (True, '', label)


    def get_stream_id(self):
        if self.num_streams > pow(2,30):
            self.num_streams = 0;
        
        return self.num_streams


    def get_active_stream_labels(self):
        return list(self.streams.keys())


    def remove_stream_output_ws(self, stream_label):
        if stream_add in self.out_stream_ws:
            del self.out_stream_ws[stream_label]
        else:
            logging.('problem removing inexisting StreamOutputWebSocket: '+stream_label)


    def add_stream_output_ws(self, stream_add, stream_label):
        self.out_stream_ws[stream_label] = stream_add
        

    def end_transmission(self, stream_label, close_from_socket):
        if stream_label not in self.streams.keys():
            return

        if not close_from_socket and self.streams.get(stream_label) is not None:
            self.streams[stream_label].close()

        if self.stream_plot[stream_label]:
            cv2.destroyAllWindows()
            cv2.waitKey(1)

        # self.stream_plot.remove(stream_label)
            
        if stream_label in self.streams.keys():
            del self.streams[stream_label]
        del self.stream_results_batch[stream_label]
        if self.stream_sliding_window.get(stream_label) is not None:
            del self.stream_sliding_window[stream_label]
        if stream_label in self.stream_temp_coherence:
            del self.stream_temp_coherence[stream_label]
        self.num_streams = self.num_streams - 1

        for seq in self.config.config_data['testSequences']:
            if seq['label'] == stream_label:
                self.config.config_data['testSequences'].remove(seq)
                break

        


    def end_transmissions(self):
        keys = list(self.streams.keys())

        for k in keys:
            self.end_transmission(k, close_from_socket = False)
        
