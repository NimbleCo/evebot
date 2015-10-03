import os
import yaml
import logging

class Config:
    def __init__(self, data):
        self._data = data
        self._logger = logging.getLogger(__name__)
        self.DEBUG = False

        if 'EVEBOT_API_TOKEN' in os.environ:
            self.set_api_token(os.environ['EVEBOT_API_TOKEN'])

    def _merge_dicts(self, a, b):
        for k in b:
            if k in a and isinstance(b[k], dict) and isinstance(a[k], dict):
                a[k] = self._merge_dicts(a[k], b[k])
            else:
                a[k] = b[k]

        return a

    def get(self, path):
        val = self._data

        for element in path.split('.'):
            if not element in val:
                raise Exception('Missing setting "%s".' % path)

            val = val[element]

        return val

    def load_yaml(self, filename):
        file = open(filename, 'r')
        cfg = yaml.load(file)
        file.close()

        if not cfg:
            return

        if not isinstance(cfg, dict):
            raise Exception('Could not parse config')

        self._data = self._merge_dicts(self._data, cfg)

    def enable_debug_mode(self):
        self.DEBUG = True

    def set_api_token(self, token):
        self._data['basic']['api_token'] = token

    def get_api_token(self):
        return self.get('basic.api_token')

    def get_log_file(self):
        return self.get('basic.log_file')

    def get_enabled_plugins(self):
        return self.get('plugins.enabled')

    def get_naughty_channels(self):
        return self.get('plugins.naughty_channels')

    def are_ims_naughty(self):
        return self.get('plugins.ims_are_naughty')

default_config = {
    'basic': {
        'log_file': None,
        'api_token': None
    },
    'core': {
        'ping_interval': 5,
        'thread_sleep_time': 0.01,
        'thread_join_timeout': 1,
        'channel_message_buffer_size': 1000,
    },
    'plugins': {
        'enabled': [
            'evebot.plugins.commands.CommandsPlugin'
        ],
        'naughty_channels': [],
        'ims_are_naughty': False
    }
}

config = Config(default_config)




