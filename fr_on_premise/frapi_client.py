from fr_on_premise import websocket_frapi
from tornado import ioloop
from threading import Thread
import json
import cv2
import time

class FrapiClient():

    def __init__(self, config_name):
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = {}
        self.stream_results = {}
        self.num_streams = 0

        # try:
        with open(config_name) as data_file:    
            config_data = json.load(data_file)
        # except:
        #     print('asfasdf')
        #     print('ERROR: problem opening config', config_name)
        #     return

        self.config_data = config_data

        self.ip = config_data['frapi']['ip']
        self.port = config_data['frapi']['port']
        self.api_key = config_data['frapi']['api_key']
        self.json_node_frames = config_data['frapi']['json_node_frames']
        self.json_dir = config_data['frapi']['json_dir']

        if self.ip is None:
            print('ERROR: Missing ip of the FrAPI server.')
            return

        if self.port is None:
            print('ERROR: Missing port of the FrAPI server.')
            return
        else:
            self.port = str(self.port)

        if self.api_key is None:
            print('ERROR: Missing api_key of the FrAPI server.')
            return

        if self.json_node_frames is None:
            self.json_node_frames = 15

        if self.json_dir is None:
            self.json_dir = './out_json/'

        for i in range(0, len(config_data['testSequences'])):
            self.transmit(config_data['testSequences'][i])


    def get_config_data(self):
        return self.config_data


    def transmit(self, config_data):
        label = self.get_stream_label(config_data)
        self.stream_results[label] = []
        self.num_streams = self.num_streams + 1

        ws_stream = websocket_frapi.WebSocketFrapi()
        ws_url = 'ws://' + self.ip + ':' + self.port + '/recognize?api_key=' + self.api_key
        ws_stream.config(config_data, ws_url, label, self)
        self.streams[label] = ws_stream


    def on_message(self, image, ores, stream_label):
        if stream_label not in self.streams:
            print('Stream', stream_label, 'already closed.')
            return
        if image is not None and 'people' in ores and stream_label in self.stream_results:
            self.plot_recognition_info(image, ores, stream_label)

            self.stream_results[stream_label].append(ores)
            if len(self.stream_results[stream_label]) >= self.json_node_frames:
                self.post_results(stream_label)
        

    def post_results(self, stream_label):
        file_name = stream_label+'_'+str(time.time())+'.json'
        if stream_label not in self.streams:
            print('Stream', stream_label, 'already closed.')
            return
        with open(self.json_dir+'/'+file_name, 'w') as fp:
            json.dump(self.stream_results[stream_label], fp, indent=4, separators=(',', ': '))

        self.stream_results[stream_label].clear()


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

        cv2.imshow(stream_label, image)
        cv2.waitKey(1)


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

        print('end_transmission', stream_label)
        if not close_from_socket:
            self.streams[stream_label].close()
            
        del self.streams[stream_label]
        del self.stream_results[stream_label]
        self.num_streams = self.num_streams - 1

        cv2.destroyAllWindows()
        cv2.waitKey(1)


    def end_transmissions(self):
        keys = list(self.streams.keys())

        for k in keys:
            self.end_transmission(k)
        
