from fr_on_premise.stream_video import *
from tornado import ioloop
from threading import Thread

class FrapiClient():

    def __init__(self, config_name):
        self.ioloop = ioloop.IOLoop.instance()
        self.streams = []
        self.stream_results = []
        self.window_name = []
        def ioloop_fun(self):
            try:
                ioloop.IOLoop.instance().start()
            except KeyboardInterrupt:
                self.end_transmissions()

        t = Thread(target = ioloop_fun, args = (self,))
        t.start()

        with open(config_name) as data_file:    
            config_data = json.load(data_file)

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


    def transmit(self, config_data):
        label = config_data['label']
        if label is None:
            label = 'Stream_'+str(len(self.streams)+1)

        self.window_name.append(label)
        self.stream_results.append([])
        stream_id = len(self.window_name)-1
        stream = StreamVideo()
        ws_url = 'ws://' + self.ip + ':' + self.port + '/recognize?api_key=' + self.api_key
        stream.config(config_data, ws_url, stream_id, self)
        self.streams.append(stream)


    def on_message(self, image, ores, stream_id):
        if image is not None and 'people' in ores:
            self.plot_recognition_info(image, ores, stream_id)

            self.stream_results[stream_id].append(ores)
            if len(self.stream_results[stream_id]) >= self.json_node_frames:
                self.post_results(stream_id)


    def post_results(self, stream_id):
        file_name = self.window_name[stream_id]+'_'+str(time.time())+'.json'
        with open(self.json_dir+'/'+file_name, 'w') as fp:
            json.dump(self.stream_results[stream_id], fp, indent=4, separators=(',', ': '))

        self.stream_results[stream_id].clear()


    def plot_recognition_info(self, image, ores, stream_id):
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

        cv2.imshow(self.window_name[stream_id], image)
        cv2.waitKey(1)
        

    def end_transmissions(self):
        for s in self.streams:
            s.close()
        


