# Common Python library imports
import time
import json

# Pip package imports
from web3 import Web3
from functools import wraps
from loguru import logger

# Internal package improts
from web3_utils.utils import Web3Provider
from .icontract import IContract, require_connected
from .token import Token

class Router(IContract):

    def _swap(self, contract_fnc, token_in: Token, token_out: Token, amount, slippage, timeout, speed):
        web3 = Web3Provider()

        current_gas = web3.eth.get_block("pending")['baseFeePerGas']
        priority = int(Web3.toWei(2 * speed, 'gwei'))
        gas_price = int(current_gas * 1.2 * speed)
        #gas_price = int(web3.eth.gas_price * 1.2 * speed)

        if gas_price < priority:
            gas_price += priority

        if not token_in.is_approved(self, amount):
            logger.info("Approving {} tokens {}".format(token_in.address, amount))
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
    def swap(self, token_in: Token, token_out: Token, amount, max_out=None, slippage=0.01, timeout=1000, speed=1, fee=None):
        web3 = Web3Provider()

        if fee is None:
            fnc = self.contract.functions.swapExactTokensForTokens
        else:
            fnc = self.contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens

        if max_out is not None:
            max_out = token_out.from_decimals(float(max_out))
            amout_out = self.get_amounts_out(amount, token_in, token_out)
            if int(amout_out) > int(max_out):
                amount = self.get_amounts_in(max_out, token_out, token_in)

        return self._swap(fnc, token_in, token_out, amount, slippage, timeout, speed)

    @require_connected
    def get_amounts_out(self, amount_in, token_in: Token, token_out : Token):
        _ , ret_val =  self.contract.functions.getAmountsOut(amount_in, [token_in.address, token_out.address]).call()
        return ret_val

    @require_connected
    def get_amounts_in(self, amount_out, token_in: Token, token_out : Token):
        ret_val, _ = self.contract.functions.getAmountsIn(amount_out, [token_out.address, token_in.address]).call()
        return ret_val