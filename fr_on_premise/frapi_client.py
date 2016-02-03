from fr_on_premise import websocket_frapi
from tornado import ioloop
from threading import Thread
from fr_on_premise.temp_coherence import TempCoherence
import json
import cv2
import time
import requests, logging
from io import StringIO
from requests_toolbelt import MultipartEncoder

class FrapiClient():

    def __init__(self):
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = {}
        self.stream_plot = {}
        self.stream_sliding_window = {}
        self.stream_temp_coherence = {}
        self.num_streams = 0
        self.config_data = None


    def config(self, config_data):
        if self.config_data is not None:
            return self.update_config(config_data)

        self.config_data = config_data

        self.ip = config_data['frapi']['ip']
        self.port = config_data['frapi']['port']
        self.api_key = config_data['frapi']['api_key']

        self.save_json_config = config_data['frapi']['output']['json']
        self.http_post_config = config_data['frapi']['output']['http_post']
        
        if self.ip is None:
            return (False, 'Missing ip of the FrAPI server.')

        if self.port is None:
            return (False, 'Missing port of the FrAPI server.')
        else:
            self.port = str(self.port)

        if self.api_key is None:
            return (False, 'Missing api_key of the FrAPI server.')

        if self.save_json_config is not None:
            self.stream_results_batch = {}
            
            if self.save_json_config['dir'] is None:
                self.save_json_config['dir'] = './out_json/'
            
            if self.save_json_config['node_frames'] is None:
                self.save_json_config['node_frames'] = 15

        if self.http_post_config is not None:
            if self.http_post_config['url'] is None:
                logging.error('Need to inform HTTP Post route if http-post was selected as output.')
                return (False, 'Need to inform HTTP Post route if http-post was selected as output.')

            if self.http_post_config['post_image'] is None:
                self.http_post_config['post_image'] = False
            

        for i in range(0, len(config_data['testSequences'])):
            self.transmit(config_data['testSequences'][i])

        return (True, '')


    def update_config(self, config_data):
        # if I have a major config change, just reset everything
        if self.ip != config_data['frapi']['ip'] or self.port != str(config_data['frapi']['port']) or\
            self.api_key != config_data['frapi']['api_key']:

            self.config_data = None
            return self.config(config_data)

        self.save_json_config = config_data['frapi']['output']['json']
        self.http_post_config = config_data['frapi']['output']['http_post']
        
        if self.save_json_config is not None:
            if self.save_json_config['dir'] is None:
                self.save_json_config['dir'] = './out_json/'
            
            if self.save_json_config['node_frames'] is None:
                self.save_json_config['node_frames'] = 15

        if self.http_post_config is not None:
            if self.http_post_config['url'] is None:
                logging.error('Need to inform HTTP Post route if http-post was selected as output.')
                return (False, 'Need to inform HTTP Post route if http-post was selected as output.')

            if self.http_post_config['post_image'] is None:
                self.http_post_config['post_image'] = False
            

        # find the streams that ended, and the ones that are new
        list_removed = []
        for old in self.config_data['testSequences']:
            if old not in config_data['testSequences']:
                list_removed.append(old)

        list_added = []
        for new_video in config_data['testSequences']:
            if new_video not in self.config_data['testSequences']:
                list_added.append(new_video)

        for old in list_removed:
            self.end_transmission(old['label'], close_from_socket = False)

        for new_video in list_added:
            self.transmit(new_video)

        self.config_data = config_data

        return (True, None)


    def get_config_data(self):
        return self.config_data


    def transmit(self, config_data):
        label = self.get_stream_label(config_data)
        self.stream_results_batch[label] = []
        self.stream_plot[label] = config_data.get('plotStream', False)
        self.stream_sliding_window[label] = config_data.get('slidingWindow', 0)
        if self.stream_sliding_window[label] > 0:
            self.stream_temp_coherence = TempCoherence(self.stream_sliding_window[label])
        self.num_streams = self.num_streams + 1

        ws_stream = websocket_frapi.WebSocketFrapi()
        ws_url = 'ws://' + self.ip + ':' + self.port + '/recognize?api_key=' + self.api_key
        ws_stream.config(config_data, ws_url, label, self)
        self.streams[label] = ws_stream


    def on_message(self, image, ores, stream_label):
        if stream_label not in self.streams:
            print('Stream', stream_label, 'already closed.')
            return
        
        if image is not None and 'people' in ores and stream_label in self.stream_results_batch:
            post_image = self.http_post_config is not None and len(ores['people']) > 0

            if post_image or self.stream_plot[stream_label]:
                debug_image = self.plot_recognition_info(image, ores, stream_label)

            if self.stream_sliding_window[stream_label] > 1 and (self.save_json_config is not None or post_image):
                ores = self.stream_temp_coherence[stream_label].add_frame(ores)

            # the output is only activate if there is someone recognized.
            if self.save_json_config is not None:
                self.stream_results_batch[stream_label].append(ores)
                if len(self.stream_results_batch[stream_label]) >= self.save_json_config['node_frames']:
                    self.save_json_results(stream_label)

            if post_image:
                self.post_result(ores, debug_image)

    def post_result(self, result, debug_image):
        """
        This function posts the result that is passed to the configured
        function. If no image is required it is a application/json payload,
        otherwise is a multiform/data.
        """
        try:
            if not self.http_post_config['post_image']:
                requests.post(self.http_post_config['url'], data=json.dumps(result), headers={'Content-type': 'application/json'})
            else:
                cv2.imwrite('debug_image.jpg', debug_image)
                m = MultipartEncoder(fields={'image': ('filename', open('debug_image.jpg', 'rb')), 
                                         'recognition': json.dumps(result)})
                res = requests.post(self.http_post_config['url'], data=m, 
                        headers={'Content-Type': m.content_type})
        except:
            logging.warn('Post result to url'+self.http_post_config['url']+' failed!');
        

    def save_json_results(self, stream_label):
        file_name = stream_label+'_'+str(time.time())+'.json'
        if stream_label not in self.streams:
            print('Stream', stream_label, 'already closed.')
            return
        with open(self.save_json_config['dir']+'/'+file_name, 'w') as fp:
            json.dump(self.stream_results_batch[stream_label], fp, indent=4, separators=(',', ': '))

        self.stream_results_batch[stream_label].clear()


    def plot_recognition_info(self, image, ores, stream_label):
        for rec in ores['people']:
            l = rec['top_left']['x']
            t = rec['top_left']['y']
            r = rec['bottom_right']['x']
            b = rec['bottom_right']['y']
            tl = [l, t]
            br = [r, b]
            cv2.rectangle(image, (int(tl[0]), int(tl[1])), (int(br[0]), int(br[1])), (165, 142, 254), 4)
            
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
        label = config_data['label']

        if label is None:
            label = 'Stream_'+str(self.get_stream_id())
            print('Error: label not defined. Seting to', label)
        if label in self.streams:
            label = 'Stream_'+str(self.get_stream_id())
            print('Error: label already defined. Seting to', label)

        return label


    def get_stream_id(self):
        if self.num_streams > pow(2,30):
            self.num_streams = 0;
        
        return self.num_streams
        

    def end_transmission(self, stream_label, close_from_socket):
        if stream_label not in self.streams:
            return

        if not close_from_socket:
            self.streams[stream_label].close()
            # if I'm closing from the frapi_client, I will enter in
            # this function again, called by stream.close(). So I'm
            # returning now, and when stream.close() call me again, 
            # the rest of the closing process will continue.
            return

        del self.streams[stream_label]
        del self.stream_results_batch[stream_label]
        self.num_streams = self.num_streams - 1

        for seq in self.config_data['testSequences']:
            if seq['label'] == stream_label:
                self.config_data['testSequences'].remove(seq)
                break

        cv2.destroyAllWindows()
        cv2.waitKey(1)


    def end_transmissions(self):
        keys = list(self.streams.keys())

        for k in keys:
            self.end_transmission(k, close_from_socket = False)
        
