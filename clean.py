import asyncio
import requests
import datetime
import time
import concurrent.futures


# from dotenv import dotenv_values
# config = dotenv_values(".env")

# async_solana_client= AsyncClient(config["RPC_HTTPS_URL"]) #Enter your API KEY in .env file

# solana_client = Client(config["RPC_HTTPS_URL"])

# LAMPORTS_PER_SOL = 1000000000
# MAX_RETRIES = 5
# RETRY_DELAY = 3

from solders.keypair import Keypair
from solanatracker import SolanaTracker

from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
import os
solana_client = Client("https://api.mainnet-beta.solana.com")

from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 从环境变量中获取密钥字符串
sol_key_base58 = os.getenv("PRIVATE_KEY")

# 使用密钥字符串创建Keypair对象
sol_key = Keypair.from_base58_string(sol_key_base58)

owner = sol_key.pubkey()


sol_addr = "So11111111111111111111111111111111111111112"
sol_amt = 0.05
mint_dec = 1000000

import sqlite3


class token:
    def __init__(self, mint, name, symbol, bondingCurve, associatedBCurve,creator,twitter,telegram) -> None:
        self.mint = mint
        self.name = name
        self.symbol = symbol
        self.bondingCurve = bondingCurve
        self.associatedBCurve = associatedBCurve
        self.creator = creator
        self.twitter = twitter
        self.telegram = telegram


last_mints = set()

def get_new_tokens():
    global last_mints
    smart_money = "HZoxemecYjge7b4fhPQw8KXA5zp7my13qeXVHyjQHD6T"

    url = "https://client-api-2-74b1891ee9f9.herokuapp.com/coins?offset=0&limit=20&sort=created_timestamp&order=DESC&includeNsfw=true"

    try:
        r = requests.get(url=url)
        r.raise_for_status()  # Raise an HTTPError if the request was not successful
        data = r.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return

    tokens = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_coin, coin) for coin in data]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                tokens.append(result)

    last_mints = {token.mint for token in tokens}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(check_dev, token.mint, token.creator,smart_money) for token in tokens]

        for future in concurrent.futures.as_completed(results):
            # Handle exceptions if any
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

def process_coin(coin):
    mint = coin['mint']
    if mint in last_mints:
        return None  # Skip if mint is in last mints

    new_token = token(coin['mint'], coin['name'], coin['symbol'], coin['bonding_curve'], coin['associated_bonding_curve'], coin['creator'], coin['twitter'], coin['telegram'])

    if new_token.twitter is not None or new_token.telegram is not None:
        if rug_check(coin['mint']) == False:
            return new_token

    return None

def rug_check(mint):
    url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{mint}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("code") == 0 and data.get("msg") == "success":
            token_data = data.get("data").get("token")
            rug_ratio = token_data.get("rug_ratio")
            holder_count = token_data.get("holder_count")

            print(
                {"mint": str(mint)},
                f"Rug Ratio: {rug_ratio} and holderCount: {holder_count}"
            )

            if rug_ratio is None:
                return False
            else:
                return rug_ratio > 0.5  # 如果 rug_ratio 大于 0.5，则返回 True，否则返回 False
    except Exception as error:
        print(f"An error occurred: {error}")
        return True


async def swap(source,des,amt):
    keypair = sol_key
    solana_tracker = SolanaTracker(keypair, "https://api.solanatracker.io/rpc")
    print("swap to " , des)
    swap_response = await solana_tracker.get_swap_instructions(
        source,  # From Token
        des,  # To Token
        amt,  # Amount to swap
        10,  # Slippage
        str(keypair.pubkey()),  # Payer public key
        0.00005,  # Priority fee (Recommended while network is congested)
        True,  # Force legacy transaction for Jupiter
    )

    txid = await solana_tracker.perform_swap(swap_response)

    # Returns txid when the swap is successful or raises an exception if the swap fails
    print("Transaction ID:", txid)
    print("Transaction URL:", f"https://explorer.solana.com/tx/{txid}")



import threading

def delete_records():
    conn = sqlite3.connect('processed_addresses.db')
    c = conn.cursor()

    # 获取删除前的记录数
    c.execute("SELECT COUNT(*) FROM processed_addresses WHERE dev_action = 'dev give up'")
    num_before_delete = c.fetchone()[0]
    print(f"Before deletion: {num_before_delete} records")

    # 执行删除操作的 SQL 查询
    c.execute('''DELETE FROM processed_addresses 
                WHERE dev_action = 'dev give up' 
                AND (SELECT COUNT(*) FROM processed_addresses) > 20''')

    conn.commit()

    # 获取删除后的记录数
    c.execute("SELECT COUNT(*) FROM processed_addresses WHERE dev_action = 'dev give up'")
    num_after_delete = c.fetchone()[0]
    print(f"After deletion: {num_after_delete} records")

    # 关闭数据库连接
    conn.close()

def check_dev(token_address, creator, smart_money):
    # 连接到数据库
    conn = sqlite3.connect('processed_addresses.db')
    c = conn.cursor()

    # 创建一个表来存储已处理的地址
    c.execute('''CREATE TABLE IF NOT EXISTS processed_addresses
                (token_address TEXT PRIMARY KEY,
                creator TEXT,
                smart_money TEXT,
                dev_action TEXT,
                num_trades INTEGER,
                current_time TEXT)''')
    
    # 检查地址是否已经处理过
    c.execute("SELECT * FROM processed_addresses WHERE token_address=?", (token_address,))
    if c.fetchone():
        conn.close()
        return

    url = f"https://client-api-2-74b1891ee9f9.herokuapp.com/trades/{token_address}?limit=5&offset=0"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data for {token_address}: {e}")
        conn.close()
        return

    if response.status_code == 200:
        trades = response.json()
        num_trades = len(trades)
        
        if num_trades < 4:
            is_buy_exist = False
            is_sell_exist = False
            for trade in trades:
                if trade["user"] == creator:
                    if trade["is_buy"] and trade["sol_amount"] < 2999999972:
                        is_buy_exist = True
                    else:
                        is_sell_exist = True

            if is_buy_exist and is_sell_exist:
                print(token_address, "dev give up")

            elif is_buy_exist:
                if smart_money in [trade["user"] for trade in trades]:
                    print(token_address, "smart money buy with dev")
                    ## TODO:buy
                    asyncio.run(swap(sol_addr,token_address,sol_amt))
                    # 将地址记录到数据库中，同时记录 creator 和 smart_money
                    c.execute("INSERT INTO processed_addresses (token_address, creator, smart_money, dev_action) VALUES (?, ?, ?, ?)", (token_address, creator, smart_money, "dev buy"))
                    conn.commit()
                else:
                    print(token_address, "dev buy")
                    ## TODO:buy
                    asyncio.run(swap(sol_addr,token_address,sol_amt))

                    # 将地址记录到数据库中，同时记录 creator 和 smart_money
                    smart_money = ""
                    c.execute("INSERT INTO processed_addresses (token_address, creator, smart_money, dev_action) VALUES (?, ?, ?, ?)", (token_address, creator, smart_money, "dev buy"))

                    conn.commit()

            elif is_sell_exist:
                print(token_address, "dev sell")


    # 关闭数据库连接
    conn.close()


def update_dev_action():
    while True:
        print("check rug")
        conn = sqlite3.connect('processed_addresses.db')
        c = conn.cursor()

        c.execute("SELECT token_address, creator, smart_money, dev_action FROM processed_addresses")
        rows = c.fetchall()

        for row in rows:
            token_address, creator, smart_money, dev_action = row

            # 如果 dev_action 已经是 "dev give up"，则跳过该 token_address
            if dev_action == "dev give up":
                continue
            time.sleep(1)

            # is_sell_exist = False
            # cata = solana_client.get_token_accounts_by_owner(Pubkey.from_string(creator), TokenAccountOpts(mint=Pubkey.from_string(token_address)))
            # if cata.value != []:
            #     camt = solana_client.get_token_account_balance(cata.value[0].pubkey).value.amount 
            #     camount = int(camt)/1000000
            #     print(token_address,"check rug 1 ",creator,"have",camount)

            #     if camount == 0:
            #         is_sell_exist = True
            #     else:
            #         continue
            print(token_address,"check rug 1 ")

            url = f"https://client-api-2-74b1891ee9f9.herokuapp.com/trades/{token_address}?limit=2000&offset=0"
            try:
                response = requests.get(url)
                response.raise_for_status()
                trades = response.json()
            except requests.RequestException as e:
                print(f"Error fetching data for {token_address}: {e}")
                continue

            if trades:
                is_sell_exist = False
                for trade in trades:
                    if trade["user"] == creator:
                        if trade["is_buy"]:
                            is_buy_exist = True
                        else:
                            is_sell_exist = True

                if is_sell_exist:
                    dev_action = "dev give up"
                    ## TODO:SELL
                    print("check rug 2 ")


                    try:
                        ata = solana_client.get_token_accounts_by_owner(owner, TokenAccountOpts(mint=Pubkey.from_string(token_address)))
                        if ata.value != []:
                            amt = solana_client.get_token_account_balance(ata.value[0].pubkey).value.amount 
                            amount = int(amt)/1000000
                            if amount == 0:
                                return
                            print(token_address,sol_addr,amount)
                            asyncio.run(swap(token_address,sol_addr,amount))
                    except Exception as e:
                        print("An error occurred in get_token_accounts_by_owner:", e)

                    # num_trades = 0
                    # if trades:
                    #     num_trades = len(trades)
                        
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间并格式化为字符串
                    c.execute("UPDATE processed_addresses SET dev_action=?, num_trades=?, current_time=? WHERE token_address=?", (dev_action, num_trades,current_time, token_address))
                    conn.commit()

        conn.close()
        print("check over")
        time.sleep(1)
        delete_records()


def clean_dev_action():
    while True:
        print("check rug")
        conn = sqlite3.connect('processed_addresses.db')
        c = conn.cursor()

        c.execute("SELECT token_address, creator, smart_money, dev_action FROM processed_addresses")
        rows = c.fetchall()

        for row in rows:
            token_address, creator, smart_money, dev_action = row

            # 如果 dev_action 已经是 "dev give up"，则跳过该 token_address
            if dev_action == "dev give up":
                continue
            time.sleep(1)

            is_sell_exist = False
            camount = 100000
            try:

                cata = solana_client.get_token_accounts_by_owner(Pubkey.from_string(creator), TokenAccountOpts(mint=Pubkey.from_string(token_address)))
                if cata.value != []:
                    camt = solana_client.get_token_account_balance(cata.value[0].pubkey).value.amount 
                    camount = int(camt)/1000000
                    print(token_address,"check rug 1 ",creator,"have",camount)
            except Exception as e:
                print("An error occurred in get_token_accounts_by_owner 1:", e)
                time.sleep(10)

            if camount < 10:
                is_sell_exist = True
                print("sell",is_sell_exist)
            else:
                continue
            # print(token_address,"check rug 1 ")

            url = f"https://client-api-2-74b1891ee9f9.herokuapp.com/trades/{token_address}?limit=2000&offset=0"
            try:
                response = requests.get(url)
                response.raise_for_status()
                trades = response.json()
            except requests.RequestException as e:
                print(f"Error fetching data for {token_address}: {e}")
                continue

            # if trades:
            #     is_sell_exist = False
            #     for trade in trades:
            #         if trade["user"] == creator:
            #             if trade["is_buy"]:
            #                 is_buy_exist = True
            #             else:
            #                 is_sell_exist = True

            if is_sell_exist:
                dev_action = "dev give up"
                ## TODO:SELL
                print("check rug 2 ")
                time.sleep(5)


                try:
                    ata = solana_client.get_token_accounts_by_owner(owner, TokenAccountOpts(mint=Pubkey.from_string(token_address)))
                    if ata.value != []:
                        amt = solana_client.get_token_account_balance(ata.value[0].pubkey).value.amount 
                        amount = int(amt)/1000000
                        if amount == 0:
                            return
                        print(token_address,sol_addr,amount)
                        asyncio.run(swap(token_address,sol_addr,amount))
                except Exception as e:
                    print("An error occurred in get_token_accounts_by_owner:", e)
                    time.sleep(5)

                num_trades = 0
                if trades:
                    num_trades = len(trades)
                    
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间并格式化为字符串
                c.execute("UPDATE processed_addresses SET dev_action=?, num_trades=?, current_time=? WHERE token_address=?", (dev_action, num_trades,current_time, token_address))
                conn.commit()

        conn.close()
        print("check over")
        time.sleep(1)
        delete_records()

## TODO: 10:00 - 12:00 为高概率区域
async def main():

    # 启动更新线程
    update_thread = threading.Thread(target=update_dev_action)

    update_thread.daemon = True
    update_thread.start()

    while True:
        get_new_tokens()
        time.sleep(3)

async def clean():

    update_thread = threading.Thread(target=clean_dev_action)
    update_thread.daemon = True
    update_thread.start()

    while True:
        time.sleep(3)


#asyncio.run(main())

asyncio.run(clean())

