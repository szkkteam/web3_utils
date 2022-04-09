import os
import sys
import web3
import json
import argparse
from datetime import datetime, timedelta
import time
from web3 import Web3
from web3_utils import Router, Token, Web3Provider, get_abi, Config, Factory, Pair

p_key = os.environ.get('PRIVATE_KEY')

def parse_args():
    parser = argparse.ArgumentParser(description='Ape bot')
    parser.add_argument('-n', '--network', help="Blockchain network")
    parser.add_argument('-s', '--speed', help="Speed multiplier for gas", default=1, type=int)
    parser.add_argument('-f', '--fee', help="Support fee", default=True, type=bool)
    parser.add_argument('-t', '--timeout', help="Timeout for swap", default=1000, type=int)

    return parser.parse_args()


def run():
    args = parse_args()
    config = Config.load(args.network)

    w3 = Web3Provider(Web3Provider.HTTPProvider(config.http_provider))
    account = w3.eth.account.privateKeyToAccount(p_key)

    #token_out_addr = input("Token name or contract address: ")

    router = Router(config.get_dex()['router']['address'], get_abi(config.get_dex()['router']['abi']), wallet=account)
    token_out = Token(config.get_token_address("0xe097bcEb09bfb18047Cf259F321cC129b7bEba5e"), get_abi("tipsy.json"), wallet=account)
    token_in = Token(config.get_token_address('wbnb'), get_abi(config.get_token_abi('wbnb')),
                     wallet=account)

    print("Waiting for launch time to set...")
    while token_out.launch_time == 0:
        time.sleep(1)


    real_launch_time = token_out.launch_time
    print("Launch time set!: ", real_launch_time)

    while True:
        if int(time.time()) >= (real_launch_time + 6):
            print("6 sec elapsed!")
            break
        else:
            time.sleep(1)

    start = time.time()
    tx = router.buy(token_in, token_out, float(Web3.toWei(1, 'ether')), speed=args.speed, timeout=args.timeout)
    print("Tx: ", tx['transactionHash'].hex())
    total = time.time() - start
    print("Time took to execute transaction: {}s".format(total))

    sys.exit(0)


    token_in = Token(config.get_token_address('weth'), get_abi(config.token_abi), wallet=account)
    token_in.approve(spender=router)

    if not token_in.is_approved:
        token_in.approve(spender=router)

    buy_amount = input("Buy amount: ")
    token_out_addr = input("Token name or contract address: ")


    start = time.time()
    token_out = Token(config.get_token_address(token_out_addr), get_abi(config.token_abi))

    if args.fee:
        tx = router.buy_with_fee(token_in, token_out, float(buy_amount), speed=args.speed, timeout=args.timeout)
    else:
        tx = router.buy(token_in, token_out, float(buy_amount), speed=args.speed, timeout=args.timeout)

    print("Tx: ", tx['transactionHash'].hex())
    total = time.time() - start
    print("Time took to execute transaction: {}s".format(total))

if __name__ == "__main__":
    run()
