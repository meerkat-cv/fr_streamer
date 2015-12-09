
import cv2
from fr_on_premise import frame_pb2


class StreamVideo:

	def __init__(self, video_filename, ws_url):
		self.video = cv2.VideoCapture(video_filename)
		self.ws_url = ws_url

	def stream(self):

		while True:
			ret, frame = self.video.read()
			f = frame_pb2.Frame()
			f.cols = 200
			f.rows = 200
			f.data = bytes(frame)
			cv2.imshow("hey", frame)
			cv2.waitKey(10)
