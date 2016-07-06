
import flask
from flask import abort, render_template
from flask.ext.classy import FlaskView, route, request
from fr_streamer.controllers.config_controller import ConfigController
from fr_streamer.views import error_view

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
        This function applies the new configuration.

        """
        (ok, error, config_data) = self.config_from_request(request)
        if not ok:
            raise error_view.InvalidParametersError(error)

        (ok, error) = self.config.change_config(config_data)
        if not ok:
            raise error_view.InternalError(error)

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

    @route('/config/modify', methods=['GET'])
    def config_post(self):
        """
        This view passes to the render all the configuration that the system
        has and applies to the form.
        """
        streams = self.config.frapi_client.config.config_data['testSequences']
        print('streams', streams)
        server_config = self.config.frapi_client.config.config_data['frapi']
        output_json = 'json' in self.config.frapi_client.config.config_data['frapi']['output']
        output_post = 'http_post' in self.config.frapi_client.config.config_data['frapi']['output']
        return render_template("modify_config.html", stream_list=streams, server_config=server_config, \
            output_json=output_json, output_post=output_post)



    @route('/stream/list', methods=['GET'])
    def config_list(self):
        """
        Reads all the streams and render a template with a list
        of configuration
        """
        streams = self.config.frapi_client.config.config_data['testSequences'];
        return render_template('list_stream.html', stream_list=streams)


