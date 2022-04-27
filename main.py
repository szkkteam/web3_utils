import os
import sys
import web3
import json
import argparse
from datetime import datetime, timedelta
import time
from web3 import Web3
from loguru import logger
from web3_utils import Router, Token, Web3Provider, get_abi, Config, Factory, Pair

p_key = os.environ.get('PRIVATE_KEY')

def parse_args():
    parser = argparse.ArgumentParser(description='Ape bot')
    parser.add_argument('-n', '--network', help="Blockchain network")
    parser.add_argument('-s', '--speed', help="Speed multiplier for gas", default=1, type=int)
    parser.add_argument('--fee', help="Support fee", action='store_true')
    parser.add_argument('--dry', help="Dry run", action='store_true')
    parser.add_argument('-t', '--timeout', help="Timeout for swap", default=1000, type=int)
    parser.add_argument('-l', '--limit', help="Multiplier limit for sell", default=2.5, type=float)
    parser.add_argument('-i', '--input_token', help="Input token sticker", default='weth')

    return parser.parse_known_args()

# TODO: Base gwei should be 1.6x
# In case of delayed launch, check for enableTrading() function call. TODO: Poll isTradingEnable variable, or configurable variable

def run():
    args, leftovers = parse_args()
    config = Config.load(args.network)

    w3 = Web3Provider(Web3Provider.HTTPProvider(config.http_provider))
    account = w3.eth.account.privateKeyToAccount(p_key)

    factory = Factory(config.get_dex()['factory']['address'], get_abi(config.get_dex()['factory']['abi']), wallet=account)
    router = Router(config.get_dex()['router']['address'], get_abi(config.get_dex()['router']['abi']), wallet=account)
    token_in = Token(config.get_token_address(args.input_token), get_abi(config.get_token_abi(args.input_token)), wallet=account)

    initial_balance = token_in.balance_with_decimal

    if not token_in.is_approved(spender=router):
        token_in.approve(spender=router)

    if args.dry:
        logger.warning("Script running in dry mode!")

    buy_amount = input("Buy amount: ")
    token_out_addr = input("Token name or contract address: ")

    script_start = time.time()
    start = time.time()
    token_out = Token(config.get_token_address(token_out_addr), get_abi(config.get_token_abi(token_out_addr)), wallet=account)

    if not args.dry:
        tx = router.swap(token_in, token_out, Web3.toWei(buy_amount, 'ether'), speed=args.speed, timeout=args.timeout, fee=args.fee)
        
        logger.info("Buy transaction completed. {}".format(tx['transactionHash'].hex()))
        total = time.time() - start
        logger.info("Time took to execute transaction {}".format(total))

        balance = token_out.balance
        logger.info("Token balance: {}".format(balance))

        token_out.approve(router, balance)
        logger.info("Token approved to sell")
    else:
        balance = router.get_amounts_out(Web3.toWei(buy_amount, 'ether'), token_in, token_out)
        logger.info("Token balance: {}".format(balance))

    prev_in_weth = 0
    while True:

        current_in_weth = router.get_amounts_out(balance, token_out, token_in)

        if prev_in_weth == current_in_weth:
            time.sleep(3)
            continue
        else:
            prev_in_weth = current_in_weth

        multiplier = float(Web3.fromWei(current_in_weth, 'ether')) / float(buy_amount)

        if multiplier >= args.limit:
            logger.info("Target multiplier hit! {:.2f}/{:.2f}".format(multiplier, args.limit))

            if not args.dry:
                start = time.time()

                tx = router.swap(token_out, token_in, token_out.balance, speed=args.speed,
                                             timeout=args.timeout, fee=args.fee)

                logger.info("Sell transaction completed. {}".format(tx['transactionHash'].hex()))
                total = time.time() - start
                logger.info("Time took to execute transaction {}".format(total))


                break

        logger.info("Token worth in weth: {:.4f} which is {:.2f}%".format(Web3.fromWei(current_in_weth, 'ether'), multiplier * 100))

    logger.info("New WETH balance: {}".format(token_in.balance_with_decimal))

    time_took_to_profit = time.time() - script_start
    profit = token_in.balance_with_decimal - initial_balance

    logger.info("{:.6f} profit made in {:.2f}s".format(profit, time_took_to_profit))

   

if __name__ == "__main__":
    run()
