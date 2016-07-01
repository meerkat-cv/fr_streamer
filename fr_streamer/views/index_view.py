
import flask
from flask import abort, render_template
from flask.ext.classy import FlaskView, route, request
from fr_streamer._version import __version__

class IndexView(FlaskView):
    route_base = '/'

    @route('/', methods=['GET'])
    def index(self):
        return render_template('index.html', version=__version__)