# Common Python library imports
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



class Web3Provider(Web3, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
