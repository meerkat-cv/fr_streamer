import base64
import flask
from flask import request, abort
from flask.ext.classy import FlaskView, route, request
from fr_streamer.controllers.frapi_client_controller import *


class StreamOutputView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.frapi_client_controller = FrapiClientController()

    @route('/stream_output', methods=['GET'])
    def plot_streams(self):
        """
        Show the all the camera streams.
        """
        labels = self.frapi_client_controller.get_stream_labels();
        stream_labels = {'label': labels}
        
        return flask.render_template("stream_output.html", stream_labels=stream_labels)

    @route('/watch/<label>', methods=['GET'])
    def plot_streams(self, label):
        """
        Show the all the camera streams.
        """
        print("label to watch: ",label)
        labels = self.frapi_client_controller.get_stream_labels();
        stream_labels = {'label': labels}
        print("stream_labels",stream_labels)
        
        return flask.render_template("stream_output.html", stream_labels=stream_labels)
        
