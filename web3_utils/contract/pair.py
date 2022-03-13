# Common Python library imports
import time
import json

# Pip package imports
from web3 import Web3
from functools import wraps

# Internal package improts
from web3_utils.utils import Web3Provider
from .icontract import IContract, require_connected
from .token import Token

class Pair(IContract):

    def get_reserves(self):
        reserve_a, reserve_b, _ = self.contract.functions.getReserves().call()
        return (reserve_a, reserve_b)

    def get_price(self):
        reserve_a, reserve_b = self.get_reserves()
        return reserve_a / reserve_b