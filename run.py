from tornado import ioloop
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler
from flask import Flask, jsonify
from flask.ext.cors import CORS
from fr_on_premise.frapi_client import FrapiClient
from fr_on_premise.video_stream import VideoStream
import tornado
import logging
import os
import sys
import time
import cv2
from threading import Thread


instance_path = os.path.dirname(os.path.realpath(__file__)) + '/config/'
app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)

def main():
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
    from fr_on_premise.views.config_view import ConfigView

    # import meerkat_frapi.views.error_views

    ConfigView.register(app)
    
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    # logging.basicConfig(
    #     level=app.config["LOG_LEVEL"], format='%(asctime)s - %(levelname)s - %(message)s')

    app.debug = app.config["APP_DEBUG"]

    tr = WSGIContainer(app)
    print('Seting up EchoWebSocket')
    tornado_application = tornado.web.Application(
    [
        (r".*", FallbackHandler, dict(fallback=tr))
    ])

    tornado_application.listen(4443)

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
        # frapi.end_transmissions()

    

if __name__ == '__main__':
    main()
