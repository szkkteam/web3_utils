import os

from .contract import (
    Token,
    Erc20,
    Router,
    Factory,
    Pair
)

from .utils import (
    Web3Provider,
    Config
)

def get_abi(*args):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi', *args)