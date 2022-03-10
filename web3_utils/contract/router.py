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

class Router(IContract):

    @require_connected
    def buy(self, token_in: Token, token_out: Token, amount, slippage=0.01, timeout=1000, speed=1):
        web3 = Web3Provider()

        gas_price = web3.eth.gas_price * speed
        priority = Web3.toWei(5*speed, 'gwei') if speed > 1 else None

        if not token_in.is_approved(self.address, Web3.toWei(amount, 'ether')):
            token_in.approve(self.address, Web3.toWei(amount, 'ether'))

        func = self.contract.functions.swapExactTokensForTokens(
            Web3.toWei(amount, 'ether'),
            0, # TODO: slippage
            [token_in.address, token_out.address],
            self._wallet.address,
            int(time.time() + timeout)
        )
        params = self._create_transaction_params(max_fee_per_gas=gas_price, max_priority_fee=priority)
        return self._send_transaction(func, params)