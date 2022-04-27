# Common Python library imports
import time
import json

# Pip package imports
from web3 import Web3
from functools import wraps

# Internal package improts
from web3_utils.utils import Web3Provider
from .icontract import IContract, require_connected
from web3_utils.utils import get_abi

class Token(IContract):

    @require_connected
    def approve(self, spender: IContract, amount=None):
        if amount is None:
            amount = self.MAX_AMOUNT

        func = self.contract.functions.approve(spender.address, int(amount))
        params = self._create_transaction_params()
        return self._send_transaction(func, params)

    @require_connected
    def is_approved(self, spender: IContract, amount=None):
        if amount is None:
            amount = self.MAX_AMOUNT

        approved_amount = self.contract.functions.allowance(self._wallet.address, spender.address).call()
        return approved_amount >= amount

    @property
    @require_connected
    def balance(self):
        return self.contract.functions.balanceOf(self._wallet.address).call()

    @property
    @require_connected
    def balance_with_decimal(self):
        return self.balance / 10**self.decimals

    @property
    def decimals(self):
        return self.contract.functions.decimals().call()

    @property
    def symbol(self):
        return self.contract.functions.symbol().call()

    @property
    def launch_time(self):
        return self.contract.functions.launchTime().call()

    def to_decimals(self, amount) -> float:
        return float(float(amount) / 10**self.decimals)

    def from_decimals(self, amount) -> int:
        return int(float(amount) * 10 ** self.decimals)

class Erc20(Token):

    def __init__(self, address, *args, **kwargs):
        super(Erc20, self).__init__(address, abi=get_abi('erc20.json'))