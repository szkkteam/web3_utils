# Common Python library imports
import os
import json
from collections.abc import MutableMapping
# Pip package imports
from web3 import Web3


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        #else:
#            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

def get_abi(*args):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi', *args)

class Web3Provider(Web3, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Config(metaclass=Singleton):

    def __init__(self, network=None, raw_config=None, *args, **kwargs):
        self.network = network
        self.store = raw_config

    @classmethod
    def load(cls, network, config_file_path=None):
        if config_file_path is None:
            config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constants.json')

        network = network.lower()

        with open(config_file_path, 'r') as fp:
            config = json.load(fp)
            assert network in config, "Unsupported network {}".format(network)
            return Config(network, config[network])

    def get_token_address(self, token_name_or_address):
        token_name_or_address = token_name_or_address.lower()

        if token_name_or_address in self.store['tokens']['items']:
            if isinstance(self.store['tokens']['items'][token_name_or_address], dict):
                return Web3.toChecksumAddress(self.store['tokens']['items'][token_name_or_address]['address'])

            return Web3.toChecksumAddress(self.store['tokens']['items'][token_name_or_address])
        return Web3.toChecksumAddress(token_name_or_address)

    @property
    def http_provider(self):
        return self.store['provider']['http']


    def get_token_abi(self, token):
        if token in self.store['tokens']['items'] and isinstance(self.store['tokens']['items'][token], dict):
            return self.store['tokens']['items'][token]['abi']
        return self.store['tokens']['abi']

    def get_dex(self, dex=None):
        if dex is None:
            dex = self.store['dex']['default']

        return self.store['dex'][dex.lower()]

