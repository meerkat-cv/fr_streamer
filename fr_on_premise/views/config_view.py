
import flask
from flask.ext.classy import FlaskView, route, request
from io import StringIO
from fr_on_premise.controllers.config_controller import ConfigController
import numpy as np
import json

# @api.route('/config')
class ConfigView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.config = ConfigController()


    def apply_config(self, request):
        """
        This function....

        """
        print('apply_config')
        (ok, error) = self.config.change_config()
        res_obj = {}

        if ok:
            res_obj = {'ping': 'pong'}
        else:
            res_obj = {'fuck': 'FUUUUCK!'}

        return flask.jsonify(res_obj)
        
            
    @route('/config/apply', methods=['POST'])
    def config_post(self):
        """
        This configures the FrAPI client using a json file.
        ---
        tags:
            - config
        parameters:
            
        responses:
            200:
                description: Configuration applied
            432:
                description: Problem on the configuration file
        """
        return self.apply_config(request)


    @route('/config/apply', methods=['GET'])
    def config_get(self):
        """
        This configures the FrAPI client using a json.
        ---
        tags:
            - config
        parameters:
            
        responses:
            200:
                description: Configuration applied
            432:
                description: Problem on the configuration
        """
        return self.apply_config(request)
