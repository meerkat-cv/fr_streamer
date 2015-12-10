
import cv2
from fr_on_premise import frame_pb2
import websocket
import numpy as np
# import jpeg


class StreamVideo:

	def __init__(self, video_filename, ws_url):
		self.video = cv2.VideoCapture(0)
		self.ws = websocket.create_connection("ws://localhost:8000/echo")

	def stream(self):
		cv2.namedWindow("hey")
		while True:
			ret, frame = self.video.read()
			# frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			_, framecomp = cv2.imencode('.jpg', frame)
			# print('framecomp', framecomp)
			# frame = np.array([[4, 3], [2, 2]], dtype=np.int32)
			# f = frame_pb2.Frame()
			# f.rows = frame.shape[0]
			# f.cols = frame.shape[1]
			msg= bytes(framecomp.tobytes())

			# j = jpeg.compress
			# vec = np.squeeze(frame)
			# for v in np.nditer(vec):
			# 	f.data.append(v.item())
			# fstr = f.SerializeToString()
			self.ws.send_binary(msg)

			# cv2.imshow("hey", frame)
			cv2.waitKey(30)
			