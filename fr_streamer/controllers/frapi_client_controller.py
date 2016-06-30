import cv2
import urllib
import numpy as np
from fr_streamer.frapi_client import FrapiClient


class FrapiClientController():
	def __init__(self):
		self.frapi_client = FrapiClient.instance()


	def get_stream_labels(self):
		stream_labels = self.frapi_client.get_active_stream_labels()

		return stream_labels
