
import cv2
from fr_on_premise import frame_pb2
import websocket


class StreamVideo:

	def __init__(self, video_filename, ws_url):
		self.video = cv2.VideoCapture(video_filename)
		self.ws = websocket.create_connection("ws://localhost:8000/echo", subprotocols=["binary", "base64"])

	def stream(self):

		while True:
			ret, frame = self.video.read()
			f = frame_pb2.Frame()
			f.rows = frame.shape[0]
			f.cols = frame.shape[1]
			f.data = bytes(frame.tobytes())
			fstr = f.SerializeToString()
			print(fstr)
			print(type(fstr))
			self.ws.send(fstr)

			# cv2.imshow("hey", frame)
			cv2.waitKey(30000)
