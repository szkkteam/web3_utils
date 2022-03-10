import os
import sys
import web3
import json
from datetime import datetime, timedelta
import time
from web3_utils import Router, Token, Web3Provider

p_key = os.environ.get('PRIVATE_KEY')
wss_provider = "wss://mainnet.infura.io/_wss"
http_provider = "https://kovan.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"

addresses = {
    'factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
    'router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    'weth': '0xd0a1e359811322d97991e03f863a0c30c2cf029c',
    'usdc': '0xc4375b7de8af5a38a93548eb8453a498222c4ff2'

}

def get_uniswap_abi(abi):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web3_utils', 'abi', 'uniswap_v2', abi)

def get_erc20():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web3_utils', 'abi', 'erc20.json')

# This is the web3 instance
w3 = Web3Provider(Web3Provider.HTTPProvider(http_provider))

account = w3.eth.account.privateKeyToAccount(p_key)

router = Router(addresses['router'], get_uniswap_abi('router.json'), wallet=account)
token_in = Token(addresses['weth'], get_erc20(), wallet=account)
token_out = Token(addresses['usdc'], get_erc20())


tx = router.buy(token_in, token_out, 0.0001)
print(tx['transactionHash'])
