
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


    def parse_content_type(self, content_type):
        """
        This function is used to extract the content type from the header.
        """
        json_type = 'application/json'
        data_type = 'multipart/form-data'
        lower_content_type = content_type.lower()

        if lower_content_type.find(json_type) >= 0:
            return json_type
        elif lower_content_type.find(data_type) >= 0:
            return data_type
        else:
            return ''


    def config_from_request(self, request):
        content_type = self.parse_content_type(request.headers['content-type'])

        if content_type != 'application/json':
            return (False, 'Bad content type', None)

        try:
            input_params = request.get_json(True)
        except:
            return (False, 'No valid JSON present', None)

        return (True, '', input_params)


    def apply_config(self, request):
        """
        This function....

        """
        (ok, error, config_data) = self.config_from_request(request)
        if error:
            abort(432)

        (ok, error) = self.config.change_config(config_data)
        if error:
            abort(432)

        return flask.jsonify({})
        
            
    @route('/config/apply', methods=['POST'])
    def config_post(self):
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
