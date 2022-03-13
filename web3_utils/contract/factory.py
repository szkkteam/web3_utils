# Common Python library imports
import time
import json

# Pip package imports
from web3 import Web3
from functools import wraps

# Internal package improts
from web3_utils.utils import Web3Provider
from .icontract import IContract, require_connected
from .pair import Pair
from .token import Token

class Factory(IContract):

    def get_pair(self, token_a: Token, token_b: Token, pair_abi):
        pair_address = self.contract.functions.getPair(token_a.address, token_b.address).call()
        return Pair(pair_address, pair_abi)
