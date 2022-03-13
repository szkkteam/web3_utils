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

    def _buy(self, contract_fnc, token_in: Token, token_out: Token, amount, slippage, timeout, speed):
        web3 = Web3Provider()

        priority = int(Web3.toWei((5 if speed > 1 else 2) * speed, 'gwei'))
        gas_price = int(web3.eth.gas_price * speed)

        if gas_price < priority:
            gas_price += priority

        if not token_in.is_approved(self, amount):
            token_in.approve(self, amount)

        func = contract_fnc(
            int(amount),
            0,  # TODO: slippage
            [token_in.address, token_out.address],
            self._wallet.address,
            int(time.time() + timeout)
        )
        params = self._create_transaction_params(max_fee_per_gas=gas_price, max_priority_fee=priority)
        return self._send_transaction(func, params)

    @require_connected
    def buy(self, token_in: Token, token_out: Token, amount, slippage=0.01, timeout=1000, speed=1):
        return self._buy(self.contract.functions.swapExactTokensForTokens, token_in, token_out, amount, slippage, timeout, speed)

    @require_connected
    def buy_with_fee(self, token_in: Token, token_out: Token, amount, slippage=0.01, timeout=1000, speed=1):
        return self._buy(self.contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens, token_in, token_out, amount, slippage,
                         timeout, speed)
