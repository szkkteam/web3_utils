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
    parser.add_argument('-s', '--speed', help="Speed multiplier for gas", default=1, type=int)
    parser.add_argument('-f', '--fee', help="Support fee", default=False, type=bool)

    return parser.parse_args()


def run():
    args = parse_args()
    config = Config.load(args.network)

    w3 = Web3Provider(Web3Provider.HTTPProvider(config.http_provider))
    account = w3.eth.account.privateKeyToAccount(p_key)


    router = Router(config.get_dex()['router']['address'], get_abi(config.get_dex()['router']['abi']), wallet=account)
    token_in = Token(config.get_token_address('weth'), get_abi(config.token_abi), wallet=account)

    if not token_in.is_approved:
        token_in.approve(spender=router)

    token_out_addr = input("Token name or contract address: ")
    buy_amount = input("Buy amount: ")

    start = time.time()
    token_out = Token(config.get_token_address(token_out_addr), get_abi(config.token_abi))

    if args.fee:
        tx = router.buy_with_fee(token_in, token_out, float(buy_amount), speed=args.speed)
    else:
        tx = router.buy(token_in, token_out, float(buy_amount), speed=args.speed)

    print("Tx: ", tx['transactionHash'].hex())
    total = time.time() - start
    print("Time took to execute transaction: {}s".format(total))

if __name__ == "__main__":
    run()
