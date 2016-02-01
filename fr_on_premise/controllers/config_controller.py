import cv2
import urllib
import numpy as np
from fr_on_premise.frapi_client import FrapiClient


class ConfigController():
	def __init__(self):
		self.frapi_client = FrapiClient()


	def change_config(self, config_data):
		print('config_data', config_data)
		(ok, error) = self.frapi_client.config(config_data)

		return (ok, error)
