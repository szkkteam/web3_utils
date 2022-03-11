import os
import sys
import web3
import json
import argparse
from datetime import datetime, timedelta
import time
from web3_utils import Router, Token, Web3Provider, get_abi, Config

p_key = os.environ.get('PRIVATE_KEY')

def parse_args():
    parser = argparse.ArgumentParser(description='Ape bot')
    parser.add_argument('-n', '--network', help="Blockchain network")

    return parser.parse_args()


def run():
    args = parse_args()
    config = Config.load(args.network)

    w3 = Web3Provider(Web3Provider.HTTPProvider(config.http_provider))
    account = w3.eth.account.privateKeyToAccount(p_key)


    router = Router(config.get_dex()['router']['address'], get_abi(config.get_dex()['router']['abi']), wallet=account)
    token_in = Token(config.get_token_address('weth'), get_abi(config.token_abi), wallet=account)

    token_out_addr = input("Token name or contract address: ")
    buy_amount = input("Buy amount: ")

    start = time.time()
    token_out = Token(config.get_token_address(token_out_addr), get_abi(config.token_abi))
    tx = router.buy(token_in, token_out, float(buy_amount), speed=3)
    print("Tx: ", tx['transactionHash'].hex())
    total = time.time() - start
    print("Time took to execute transaction: {}s".format(total))

if __name__ == "__main__":
    run()
