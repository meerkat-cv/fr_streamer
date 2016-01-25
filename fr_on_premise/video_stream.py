import json
import time
import cv2
import os
from pprint import pprint


class VideoStream():

    def __init__(self):
        pass
        

    def read_video_stream(self, config_file):
        with open(config_file) as data_file:    
            data = json.load(data_file)

        pprint(data)

        if data.get('video_file') is not None:
            return VideoFile(data)

        if data.get('image_dir') is not None:
            return ImageDir(data)

        if data.get('camera_url') is not None:
            return CameraUrl(data)

        print('VideoStream input type not valid.')


    def get_next_frame(self):
        print('You are using VideoStream wrong.')



class VideoFile(VideoStream):

    def __init__(self, config_data):
        self.step_frame = 1
        self.start_frame = 1
        self.curr_frame = 0
        self.open(config_data['video_file'])

        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']
            self.curr_frame = self.start_frame - 1
            self.skip_frames(self.start_frame - 1)

        if config_data.get('step_frame') is not None:
            self.step_frame = config_data['step_frame']

        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']


    def open(self, video_name):
        self.video = cv2.VideoCapture(video_name)
        if self.video.isOpened() == False:
            print('problem opening', video_name)


    def skip_frames(self, num_frames):
        for i in range(0,num_frames):
            self.curr_frame = self.curr_frame+1
            ret, frame = self.video.read()
        

    def close(self):
        self.video.release()


    def get_next_frame(self):
        self.skip_frames(self.step_frame-1)

        ret, frame = self.video.read()
        self.curr_frame = self.curr_frame+1

        return frame



class ImageDir(VideoStream):

    def __init__(self, config_data):
        self.step_frame = 1
        self.start_frame = 1
        self.curr_frame = 0
        self.files = []
        
        self.open(config_data['image_dir'])
        
        if config_data.get('begin_frame') is not None:
            self.start_frame = config_data['begin_frame']
            self.curr_frame = self.start_frame - 1
            self.skip_frames(self.start_frame - 1)

        if config_data.get('step_frame') is not None:
            self.step_frame = config_data['step_frame']

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
                print(file)
                self.files.append(image_dir + '/' + file)

        self.files.sort()
        

    def close(self):
        pass


    def get_next_frame(self):
        self.skip_frames(self.step_frame-1)

        if self.curr_frame >= len(self.files):
            return None

        frame = cv2.imread(self.files[self.curr_frame])
        self.curr_frame = self.curr_frame+1

        return frame


class CameraUrl(VideoStream):

    def __init__(self, config_data):
        self.curr_frame = 0
        self.open(config_data['camera_url'])


    def open(self, camera_url):
        if camera_url == '0':
            self.video = cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture(camera_url)

        if self.video.isOpened() == False:
            print('VideoStream::get_next_frame() -- problem opening', camera_url)
        

    def close(self):
        self.video.release()


    def get_next_frame(self):
        ret, frame = self.video.read()
        self.curr_frame = self.curr_frame+1

        if frame is None:
            print("VideoStream::get_next_frame() -- problem reading frame.")

        return frame


