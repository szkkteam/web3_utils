import os
import sys
import web3
import json
from datetime import datetime, timedelta
import time
from web3 import Web3, EthereumTesterProvider


p_key = os.environ.get('PRIVATE_KEY')
wss_provider = "wss://mainnet.infura.io/_wss"
http_provider = "https://kovan.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"

addresses = {
    'factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
    'router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    'weth': '0xd0a1e359811322d97991e03f863a0c30c2cf029c',
    'usdc': '0xc4375b7de8af5a38a93548eb8453a498222c4ff2'

}

def get_abi():
    ret = {}
    current = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current, 'abi', 'uniswap_factory_abi.json'), 'r') as fp:
        ret['factory'] = json.load(fp)['abi']
    with open(os.path.join(current, 'abi', 'uniswap_router_abi.json'), 'r') as fp:
        ret['router'] = json.load(fp)['abi']
    with open(os.path.join(current, 'abi', 'uniswap_pair_abi.json'), 'r') as fp:
        ret['pair'] = json.load(fp)['abi']
    with open(os.path.join(current, 'abi', 'erc20_abi.json'), 'r') as fp:
        ret['erc20'] = json.load(fp)['abi']
    return ret

abi = get_abi()
# This is the web3 instance
w3 = Web3(Web3.HTTPProvider(http_provider))


account = w3.eth.account.privateKeyToAccount(p_key)

factory = w3.eth.contract(w3.toChecksumAddress(addresses['factory']), abi=abi['factory'])
router = w3.eth.contract(w3.toChecksumAddress(addresses['router']), abi=abi['router'])
weth_contract = w3.eth.contract(w3.toChecksumAddress(addresses['weth']), abi=abi['erc20'])

print("Account address: ", account.address)
print("Balance: ", w3.fromWei(w3.eth.get_balance(account.address), 'ether'))
result = factory.functions.allPairsLength().call()
print(result)

# TODO: to check allowed amount https://ethereum.stackexchange.com/questions/98924/using-pyuniswap-py-and-web3-py-transaction-error

pair_addres = factory.functions.getPair(
    w3.toChecksumAddress(addresses['weth']), w3.toChecksumAddress(addresses['usdc'])
).call()
print("Pair: ", pair_addres)

pair_contract = w3.eth.contract(pair_addres, abi=abi['pair'])

reserve0, reserve1, _ = pair_contract.functions.getReserves().call()
print("Reserve0: ", reserve0)
print("Reserve1: ", reserve1)

"""
key = weth_contract.functions.approve(w3.toChecksumAddress(addresses['router']), w3.toWei(1, 'ether')).buildTransaction({'nonce': w3.eth.getTransactionCount(account.address)})
signed_tx = w3.eth.account.signTransaction(key, account.privateKey)
tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
print("TX Hash: ", tx_hash)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("TX receipt: ", tx_receipt)
"""
print("Nonce: ", w3.eth.get_transaction_count(account.address))
print(w3.eth.gas_price)

"""
estimate = router.functions.swapExactTokensForTokens(
    #w3.toWei(0.00001, 'ether'),
    1,
    0,
    [w3.toChecksumAddress(addresses['weth']), w3.toChecksumAddress(addresses['usdc'])],
    w3.toChecksumAddress(account.address),
    int(time.time()) + 1000,
).estimateGas()
print("Estimate: ", estimate)
"""

key = router.functions.swapExactTokensForTokens(
    #w3.toWei(0.00001, 'ether'),
    1,
    0,
    [w3.toChecksumAddress(addresses['weth']), w3.toChecksumAddress(addresses['usdc'])],
    w3.toChecksumAddress(account.address),
    int(time.time()) + 1000,
).buildTransaction({
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 210000,
    #'gasPrice': w3.toWei('1', 'gwei'),
    'maxFeePerGas': 20000000000, 'maxPriorityFeePerGas': 1000000000
})
print("key: ", key)

#print(key.estimateGas())

#sys.exit(0)
signed_tx = w3.eth.account.sign_transaction(key, account.privateKey)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("TX Hash: ", tx_hash)

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("TX receipt: ", tx_receipt)
