import json
import logging
import threading

class Singleton(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class Config(Singleton):

    def __init__(self):
        self.min_confidence = 0
        self.config_data = None
        self.save_json_config = None
        self.http_post_config = None
        self.ip = None
        self.port = None
        self.api_key = None
        self.save_json_config = None
        self.http_post_config = None


    def frapi_missing_config(self, config_data):
        if config_data.get('frapi') is None:
            return 'Missing frapi configuration.'

        if config_data['frapi'].get('ip') is None:
            return 'Missing ip of the FrAPI server.'

        if config_data['frapi'].get('port') is None:
            return 'Missing port of the FrAPI server.'
        
        if config_data['frapi'].get('api_key') is None:
            return 'Missing api_key of the FrAPI server.'


    def config(self, config_data):
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


    def update_config(self, config_data):
        # if I have a major config change, just reset everything
        if self.ip != config_data['frapi']['ip'] or self.port != str(config_data['frapi']['port']) or\
            self.api_key != config_data['frapi']['api_key']:

            self.config_data = None
            return self.config(config_data)

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
        for seq in config_data['testSequences']:
            if seq.get('label') is not None:
                new_labels.append(seq.get('label'))

        old_labels = self.streams.keys()
        for old in old_labels:
            if old not in new_labels:
                list_removed.append(old)

        list_added = []
        for new_video in config_data['testSequences']:
            if new_video.get('label') is None:
                continue
            if new_video['label'] not in old_labels:
                list_added.append(new_video)

        for new_video in list_added:
            (ok, error) = self.transmit(new_video)
            if not ok:
                logging.error(error)

        self.config_data = config_data

        return (True, None, list_added, list_removed)