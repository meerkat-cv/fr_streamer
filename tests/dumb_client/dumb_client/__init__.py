from tornado import ioloop
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler
from flask import Flask, jsonify
from flask.ext.cors import CORS
from dumb_client.main_client import MainClient
import tornado
import logging
import os
import sys
import time
import cv2
from threading import Thread


instance_path = os.path.dirname(os.path.realpath(__file__)) + '/../../../config/'
app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)

def build_app():
    server_env = os.getenv('SERVER_ENV')
    envs = {'production': 'production.py', 'development': 'development.py'}

    env_file = ''
    if server_env is None or server_env not in envs.keys():
        logging.warning(
            'No SERVER_ENV variable found. Assuming development...')
        env_file = envs['development']
    else:
        env_file = envs[server_env.lower().strip()]

    app.config.from_pyfile(env_file)
    CORS(app)
    # from meerkat_frapi.controllers.base_controller import ReverseProxied
    # app.wsgi_app = ReverseProxied(app.wsgi_app)

    # print('Registering views')
    # from dumb_client.views.streamer_debug_view import StreamerDebugView
    
    # StreamerDebugView.register(app)
    
    app.debug = app.config["APP_DEBUG"]

    tr = WSGIContainer(app)
    tornado_application = tornado.web.Application(
    [
        (r".*", FallbackHandler, dict(fallback=tr))
    ])
    
    main_client = MainClient()
    main_client.run()

    return tornado_application
