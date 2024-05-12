from solders.keypair import Keypair
from solanatracker import SolanaTracker
# from solana.rpc.api import Client
from solders.pubkey import Pubkey

# # 初始化 Solana 客户端
# client = Client("https://api.mainnet-beta.solana.com")

# # 要查询的账户地址
# account_address = "8ZeubP1FD4ZunFYhyB6UWhQHVuGenVXpgBCPxLA8gkJa"

# # pubkey = Pubkey.from_string("7fUAJdStEuGbc3sM84cKRL6yYaaSstyLSU4ve5oovLS7")
# # client.get_token_account_balance(pubkey).value.amount
# owner = Pubkey.from_string("8ZeubP1FD4ZunFYhyB6UWhQHVuGenVXpgBCPxLA8gkJa")
# mint = Pubkey.from_string("9KVknx2DMebvVDN82NFBjQBVyPqqtBcbhABU824To5PY")
# ata = client.get_token_accounts_by_owner(owner, mint, commitment=None)
# # 要查询的 Token 地址
# print(ata)
# 构建查询账户余额的请求
# response = client.get_token_account_balance(Pubkey("8ZeubP1FD4ZunFYhyB6UWhQHVuGenVXpgBCPxLA8gkJa"), token_address)
# # 提取余额
# balance = response["result"]["value"]["amount"]

# print(f"Account {account_address} holds {balance} tokens of {token_address}")


from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
solana_client = Client("https://api.mainnet-beta.solana.com")
owner = "8ZeubP1FD4ZunFYhyB6UWhQHVuGenVXpgBCPxLA8gkJa"
# mint = "4j3AVXkUaeUNYgmBTx3JydoYa8R6xVhtc3bjT117RiV1"
from utils import get_coin_data, get_token_balance, confirm_txn
from spl.token.instructions import create_associated_token_account, get_associated_token_address
# from pump_fun import buy,sell

async def swap(mint_str):
    # mint_str = "9mCuHECgRUdaUNFeG9xfLoquzBDE2Bx4hvvK3B8tY3w1"
    # mint = Pubkey.from_string(mint_str)
    #     # Calculate token account
    # # token_account = get_associated_token_address(owner, mint)
    # decimal = int(solana_client.get_account_info_json_parsed(mint).value.data.parsed['info']['decimals'])
    # token_balance = get_token_balance(mint_str)
    # amount = int(token_balance * 10**decimal)
    # print(amount)
    ata = solana_client.get_token_accounts_by_owner(Pubkey.from_string(owner), TokenAccountOpts(mint=Pubkey.from_string(mint_str)))
    # print(ata)
    if ata.value != []:
        amount = solana_client.get_token_account_balance(ata.value[0].pubkey).value.amount 

        print(mint_str,amount)
    if int(amount) == 0:
        return
    keypair = Keypair.from_base58_string("")

    solana_tracker = SolanaTracker(keypair, "https://rpc.solanatracker.io/public?advancedTx=true")

    swap_response = await solana_tracker.get_swap_instructions(
        mint_str,
        "So11111111111111111111111111111111111111112",  # From Token
        int(amount)/1000000,  # Amount to swap
        10,  # Slippage
        str(keypair.pubkey()),  # Payer public key
        0.00005,  # Priority fee (Recommended while network is congested)
        True,  # Force legacy transaction for Jupiter
    )

    txid = await solana_tracker.perform_swap(swap_response)

    if not txid:
        # Add retries / handle error as needed
        raise Exception("Swap failed")

    # Returns txid when the swap is successful or raises an exception if the swap fails
    print("Transaction ID:", txid)
    print("Transaction URL:", f"https://explorer.solana.com/tx/{txid}")

if __name__ == "__main__":
    import asyncio
    mints = ["HnsPPCErYJ1Pki6H8PNse3cHHgtjDxe9Tn25roEjcFr7"
             ,"EnnEU4AWTfyLLZbCRtw9gznmj21YvJXZ2mKH5rnMJWi5",
             "i7UgCWF76WU8Fdz6KzSeA4ZXSJfNczwvCfir7JPsiFp",
             "P5Dtku7NfoCjTSQtE4CjHDka1CnYQhBbkRN6et7Po4e",
             "EX1SDHGGF1TYvRAybqgaqYZmLQBJSXugRLeV2YXKGXM3",
             "GttKWVJ7uYBcFKraM2pJx4YTUUHYUGVKkt5qwZ3bMKz2",
             "GJxXpJ7DBX9aNEqVLfZAuuSLp6ATUPBdUKB6kfFX3RK2",
             "3FbEvF6H8LeCbGXKEh1YXEGghinoN6JLwX8vpNZwHyD1",
             "HwivNKJs2hTvxkCg8cMpE86GUnb9H2cmAEg5z1g3cUKE",
             "2vz2cv7JRH4zNDvMjpgeDRLQw75biBi93BmkX1NBYdoE",
             "3p2V4D4hnhTmwegx7nkNcAwsC3853n4H6pdrJ1MSv81D",
             "HiVwSQ1HWzyHagQoRQBotwaWZLzawTLLh3p8ASikTf6Z",
             "14C51KQN2RnNS6FvDPgXa9qsMwEWWYpS4AivFzJg7b9y",
             "3B7jtd3iKxJkeXcPWUf9iNBRkwSE6xhGWnMu7f6EFJUU",
             "CA2B2h1BCTFbeMHD5P1WNM41tJqW15Lbtni72az5chGJ",
             "CwUwWS6CaGE66NpLLQ26b5mozSSFsz1b9eHoGnENe4Vo",
             "AFeTVWsBbZWnuxM7qJozKK3JaTQ2EY6Hi6aV2rFMiXbe",
             "2XA1NV6jV3t3pxsqBonbg7ucJww2LWwgtuTkzYhgsmbe"]
    for mt in mints:
        asyncio.run(swap(mt))
        # sell(mt)
