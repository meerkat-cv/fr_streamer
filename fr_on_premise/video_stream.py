import json
import time
import cv2
import os
from pprint import pprint
from threading import Thread, Lock


def load_from_config(config_data):
    """ 
    This functions is like a constructor from the config that will
    return the appropirated VideoStream.
    """
    if 'video_file' in config_data:
        return VideoFile(config_data)
    if 'image_dir' in config_data:
        return ImageDir(config_data)
    if 'camera_url' in config_data:
        return CameraUrl(config_data)

    print('VideoStream input type not valid.')



class VideoStream():

    def __init__(self):
        is_opened = False
        self.curr_frame = 0
        self.end_frame = -1
        

    def read_video_stream_config_file(self, config_file):
        with open(config_file) as data_file:    
            config_data = json.load(data_file)

        self.read_video_stream(config_data)


    def get_next_frame(self):
        print('You are using VideoStream wrong.')

    def is_opened(self):
        print('You are using VideoStream wrong.')

    def isOpened(self):
        return self.is_opened

    def has_ended(self):
        if self.end_frame <= 0:
            return False
        elif self.curr_frame < self.end_frame:
            return False
        else:
            return True


    



class VideoFile(VideoStream):

    def __init__(self, config_data):
        self.step_frame = 1
        self.start_frame = 1
        self.end_frame = -1
        self.curr_frame = 0
        self.is_opened = False
        self.open(config_data['video_file'])

        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']
            self.curr_frame = self.start_frame - 1
            self.skip_frames(self.start_frame - 1)

        if config_data.get('step_frame') is not None:
            self.step_frame = config_data['step_frame']

        if config_data.get('end_frame') is not None:
            self.end_frame = config_data['end_frame']

        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']


    def open(self, video_name):
        self.video = cv2.VideoCapture(video_name)
        if self.video.isOpened() == False:
            print('VideoStream::open() -- problem opening', video_name)
        else:
            self.is_opened = True


    def skip_frames(self, num_frames):
        for i in range(0,num_frames):
            self.curr_frame = self.curr_frame+1
            ret, frame = self.video.read()
        

    def close(self):
        self.video.release()


    def get_next_frame(self):
        if self.is_opened == False or self.has_ended():
            return None

        self.skip_frames(self.step_frame-1)

        ret, frame = self.video.read()
        self.curr_frame = self.curr_frame+1

        if frame is None:
            is_opened = False

        return frame



class ImageDir(VideoStream):

    def __init__(self, config_data):
        self.step_frame = 1
        self.start_frame = 1
        self.end_frame = -1
        self.curr_frame = 0
        self.is_opened = False
        self.files = []
        
        self.open(config_data['image_dir'])
        
        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']
            self.curr_frame = self.start_frame - 1
            self.skip_frames(self.start_frame - 1)

        if config_data.get('step_frame') is not None:
            self.step_frame = config_data['step_frame']

        if config_data.get('end_frame') is not None:
            self.end_frame = config_data['end_frame']

        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']


    def skip_frames(self, num_frames):
        self.curr_frame = self.curr_frame+num_frames


    def open(self, image_dir):
        for file in os.listdir(image_dir):
            file_ext = os.path.splitext(image_dir+'/'+file)[1]
            file_ext = file_ext.lower()
            if file_ext == ".jpg" or file_ext == ".jpeg" or \
                file_ext == ".png" or file_ext == ".bmp" or file_ext == ".tiff":
                self.files.append(image_dir + '/' + file)

        self.files.sort()
        if len(files) > 0:
            self.is_opened = True
        

    def close(self):
        pass


    def get_next_frame(self):
        self.skip_frames(self.step_frame-1)

        if self.curr_frame >= len(self.files) or self.is_opened == False or self.has_ended():
            self.is_opened = False
            return None

        frame = cv2.imread(self.files[self.curr_frame])
        self.curr_frame = self.curr_frame+1

        return frame


class CameraUrl(VideoStream):

    def __init__(self, config_data):
        self.curr_frame = 0
        self.end_frame = -1
        self.frame = None
        self.is_opened = False
        self.mutex = Lock()
        self.open(config_data['camera_url'])

        if config_data.get('end_frame') is not None:
            self.end_frame = config_data['end_frame']


    def open(self, camera_url):
        if camera_url == '0':
            self.video = cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture(camera_url)

        if self.video.isOpened() == False:
            print('VideoStream::open() -- problem opening', camera_url)
        else:
            self.is_opened = True

        def capture_thread(self):
            if self.is_opened == False:
                return
            
            while self.is_opened:
                self.mutex.acquire()
                ret, self.frame = self.video.read()
                self.mutex.release()
                self.curr_frame = self.curr_frame+1
                if self.frame is None:
                    self.is_opened = False

                time.sleep(0.015)

        t = Thread(target = capture_thread, args=(self,))
        t.daemon = True
        t.start()
        
        # I'm waiting for the camera to start receiving. Otherwise, if 
        # get_next_frame is called before that, it will return an invalid
        # image
        start = time.time()
        while self.frame is None and (time.time()-start) < 5:
            time.sleep(0.05)
        

    def close(self):
        self.is_opened = False
        self.video.release()


    def get_next_frame(self):
        if self.is_opened == False or self.has_ended():
            return None

        self.mutex.acquire()
        frame_cpy = self.frame.copy()
        self.mutex.release()

        return frame_cpy


