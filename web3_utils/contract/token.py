# Common Python library imports
import time
import json

# Pip package imports
from web3 import Web3
from functools import wraps

# Internal package improts
from web3_utils.utils import Web3Provider
from .icontract import IContract, require_connected

class Token(IContract):

    @require_connected
    def approve(self, spender, amount=None):
        if amount is None:
            amount = self.MAX_AMOUNT

        func = self.contract.functions.approve(spender, amount)
        params = self._create_transaction_params()
        return self._send_transaction(func, params)

    @require_connected
    def is_approved(self, spender, amount):
        if amount is None:
            amount = self.MAX_AMOUNT

        approved_amount = self.contract.functions.allowance(self._wallet.address, spender).call()
        return approved_amount >= amount