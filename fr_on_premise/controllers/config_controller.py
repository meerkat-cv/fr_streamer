import cv2
import urllib
import numpy as np
from fr_on_premise.frapi_client import FrapiClient


class ConfigController():
	def __init__(self):
		self.frapi_client = FrapiClient('config/config.json')


	def change_config(self):
		print('changing config')
		ok = True
		error = None

		return (ok, error)
