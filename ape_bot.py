import os
import sys
import web3
import json
import argparse
from datetime import datetime, timedelta
import time
from loguru import logger
from web3 import Web3
from web3_utils import Router, Token, Web3Provider, get_abi, Config, Factory, Pair

p_key = os.environ.get('PRIVATE_KEY')

def parse_args():
    parser = argparse.ArgumentParser(description='Ape bot')
    parser.add_argument('-n', '--network', help="Blockchain network")
    parser.add_argument('-s', '--speed', help="Speed multiplier for gas", default=1, type=int)
    parser.add_argument('--fee', help="Support fee", action='store_true')
    parser.add_argument('-t', '--timeout', help="Timeout for swap", default=1000, type=int)
    parser.add_argument('-i', '--input_token', help="Input token sticker", default='weth')

    return parser.parse_known_args()


def run():
    args, leftovers = parse_args()
    config = Config.load(args.network)

    w3 = Web3Provider(Web3Provider.HTTPProvider(config.http_provider))
    account = w3.eth.account.privateKeyToAccount(p_key)

    router = Router(config.get_dex()['router']['address'], get_abi(config.get_dex()['router']['abi']), wallet=account)
    token_in = Token(config.get_token_address(args.input_token), get_abi(config.get_token_abi(args.input_token)), wallet=account)

    #if not token_in.is_approved(spender=router):
    #    token_in.approve(spender=router)

    buy_amount = input("Buy amount: ")
    max_amount = input("Max output amount: ")
    token_out_addr = input("Token name or contract address: ")

    if max_amount == "":
        max_amount = None

    start = time.time()
    token_out = Token(config.get_token_address(token_out_addr), get_abi(config.get_token_abi(token_out_addr)), wallet=account)

    tx = router.swap(token_in, token_out, Web3.toWei(buy_amount, 'ether'), max_out=max_amount, speed=args.speed, timeout=args.timeout, fee=args.fee)

    logger.info("Tx: {}".format(tx['transactionHash'].hex()))
    total = time.time() - start
    logger.info("Time took to execute transaction: {}s".format(total))

    logger.info("Token balance: {}".format(token_out.balance_with_decimal))

if __name__ == "__main__":
    run()
