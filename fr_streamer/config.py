import json
import logging
import threading
from threading import Thread, Lock


class Config():

    def __init__(self):
        self.min_confidence = 0
        self.config_data = None
        self.save_json_config = None
        self.http_post_config = None
        self.ip = None
        self.port = None
        self.api_key = None
        

    def frapi_missing_config(self, config_data):
        if config_data.get('frapi') is None:
            return 'Missing frapi configuration.'

        if config_data['frapi'].get('ip') is None:
            return 'Missing ip of the FrAPI server.'

        if config_data['frapi'].get('port') is None:
            return 'Missing port of the FrAPI server.'
        
        if config_data['frapi'].get('api_key') is None:
            return 'Missing api_key of the FrAPI server.'


    def redo_config(self, config_data):
        # make sure the config file is ok
        try:
            self.ip = config_data['frapi']['ip']
            self.port = str(config_data['frapi']['port'])
            self.api_key = config_data['frapi']['api_key']
        except KeyError:
            error = self.frapi_missing_config(frapi_cfg)
            logging.error(error)
            return (False, error)

        if self.config_data is not None:
            return self.update_config(config_data)

        if config_data['frapi'].get('output') is not None:
            self.save_json_config = config_data['frapi']['output'].get('json', None)
            self.http_post_config = config_data['frapi']['output'].get('http_post', None)

        self.config_data = config_data
        self.min_confidence = config_data['frapi'].get('minConfidence', 0)

        if self.save_json_config is not None:
            self.stream_results_batch = {}
            
            if self.save_json_config['dir'] is None:
                self.save_json_config['dir'] = './out_json/'
            
            if self.save_json_config['node_frames'] is None:
                self.save_json_config['node_frames'] = 15

        if self.http_post_config is not None:
            if self.http_post_config['url'] is None:
                logging.error('Need to inform HTTP Post route if http-post was selected as output.')
                return (False, 'Need to inform HTTP Post route if http-post was selected as output.')

            if self.http_post_config['post_image'] is None:
                self.http_post_config['post_image'] = False
            

        list_streams = []
        for new_video in config_data['testSequences']:
            list_streams.append(new_video)

        return (True, '', list_streams, [])


    def update_config(self, config_data, running_streams=[], running_streams_url=[]):
        # if I have a major config change, just reset everything
        if self.ip != config_data['frapi']['ip'] or self.port != str(config_data['frapi']['port']) or\
            self.api_key != config_data['frapi']['api_key']:

            self.config_data = None
            (ok, error, list_added, list_removed) = self.redo_config(config_data)
            return (ok, error, list_added, list_removed)

        if config_data['frapi'].get('output') is not None:
            self.save_json_config = config_data['frapi']['output'].get('json', None)
            self.http_post_config = config_data['frapi']['output'].get('http_post', None)
        else:
            self.save_json_config = None
            self.http_post_config = None

        self.min_confidence = config_data['frapi'].get('minConfidence', 0)
        
        if self.save_json_config is not None:
            if self.save_json_config['dir'] is None:
                self.save_json_config['dir'] = './out_json/'
            
            if self.save_json_config['node_frames'] is None:
                self.save_json_config['node_frames'] = 15

        if self.http_post_config is not None:
            if self.http_post_config['url'] is None:
                logging.error('Need to inform HTTP Post route if http-post was selected as output.')
                return (False, 'Need to inform HTTP Post route if http-post was selected as output.', None, None)

            if self.http_post_config['post_image'] is None:
                self.http_post_config['post_image'] = False
            

        # find the streams that ended, and the ones that are new
        list_removed = []
        new_labels = []
        new_urls = []
        for seq in config_data['testSequences']:
            if seq.get('label') is not None:
                new_labels.append(seq.get('label'))
                if seq.get('video_file') is not None:
                    new_urls.append(seq['video_file'])
                elif seq.get('camera_url') is not None:
                    new_urls.append(seq['camera_url'])
                elif seq.get('image_dir') is not None:
                    new_urls.append(seq['image_dir'])
                else:
                    new_urls.append('')

        old_labels = running_streams
        old_urls = running_streams_url

        for i in range(0,len(old_labels)):
            old_url = old_urls[i]
            old_label = old_labels[i]
            old_remains = False
            for j in range(0,len(new_labels)):
                # If I change the url or the label, restart the stream
                if old_url == new_urls[j] and old_label == new_labels[j]:
                    old_remains = True
                    break

            if old_remains == False:
                list_removed.append(old_label)


        list_added = []
        for i in range(0,len(new_labels)):
            new_url = new_urls[i]
            new_label = new_labels[i]
            add_stream = True
            for j in range(0,len(old_labels)):
                if new_url == old_urls[j] and new_label == old_labels[j]:
                    add_stream = False
                    break

            if add_stream:
                for seq in config_data['testSequences']:
                    if seq.get('label') == new_label:
                        list_added.append(seq)
                        break

        self.config_data = config_data

        return (True, None, list_added, list_removed)