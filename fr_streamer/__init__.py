from tornado import ioloop
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler
from flask import Flask, jsonify
from flask.ext.cors import CORS
from fr_streamer.frapi_client import FrapiClient
from fr_streamer.video_stream import VideoStream
import tornado
import logging
import os
import sys
import time
import cv2
from threading import Thread


instance_path = os.path.dirname(os.path.realpath(__file__)) + '/../config/'
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

    print('Registering views')
    from fr_streamer.views.config_view import ConfigView
    from fr_streamer.views.stream_output_view import StreamOutputView
    from fr_streamer.views.index_view import IndexView
    import fr_streamer.views.error_view

    ConfigView.register(app)
    StreamOutputView.register(app)
    IndexView.register(app)
    print('done.')
    
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    # logging.basicConfig(
    #     level=app.config["LOG_LEVEL"], format='%(asctime)s - %(levelname)s - %(message)s')

    app.debug = app.config["APP_DEBUG"]

    from fr_streamer.ws.stream_output_ws import StreamOutputWebSocket
    tr = WSGIContainer(app)
    tornado_application = tornado.web.Application(
    [
        (r"/stream_ws", StreamOutputWebSocket),
        (r".*", FallbackHandler, dict(fallback=tr))
    ])
    

    return tornado_application
