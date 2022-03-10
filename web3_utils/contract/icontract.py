# Common Python library imports
import json
# Pip package imports
from web3 import Web3
from functools import wraps
# Internal package improts
from web3_utils.utils import Web3Provider


def require_connected(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            raise RuntimeError('Please connect the wallet first!')
        return func(self, *args, **kwargs)

    return wrapper

class IContract (object):
    MAX_AMOUNT = int('0x' + 'f' * 64, 16)

    def __init__(self, address, abi, *args, **kwargs):
        web3 = Web3Provider()

        self._wallet = kwargs.get('wallet', None)
        self.gas_limit = 210000
        self.address = Web3.toChecksumAddress(address)
        self.contract = web3.eth.contract(self.address, abi=self._get_abi(abi))

    def _get_abi(self, path):
        with open(path, 'r') as fp:
           d = json.load(fp)
           if 'abi' in d:
               return d['abi']
           else:
               return d

    def connect_wallet(self, wallet):
        self._wallet = wallet

    def is_connected(self):
        return False if not self._wallet else True

    @require_connected
    def _send_transaction(self, func, params):
        web3 = Web3Provider()

        tx = func.buildTransaction(params)
        signed_tx = web3.eth.account.sign_transaction(tx, self._wallet.privateKey)
        receipt = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return web3.eth.wait_for_transaction_receipt(receipt)

    @require_connected
    def _create_transaction_params(self, value=0, max_fee_per_gas=None, max_priority_fee=None, gas_limit=None):
        web3 = Web3Provider()

        if not gas_limit:
            gas_limit = self.gas_limit
        if not max_priority_fee:
            max_priority_fee = Web3.toWei(1.5, 'gwei')
        if not max_fee_per_gas:
            max_fee_per_gas = web3.eth.gas_price + max_priority_fee

        return {
            'from': self._wallet.address,
            'value': value,
            'gas': gas_limit,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee,
            #'maxFeePerGas': 20000000000, 'maxPriorityFeePerGas': 1000000000,
            'nonce': web3.eth.getTransactionCount(self._wallet.address)
        }
