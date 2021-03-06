import cv2
import urllib
import numpy as np
from fr_streamer.frapi_client import FrapiClient


class ConfigController():
	def __init__(self):
		self.frapi_client = FrapiClient.instance()


	def change_config(self, config_data):
		(ok, error) = self.frapi_client.update_config(config_data)

		return (ok, error)
