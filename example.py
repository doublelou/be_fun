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
owner = "5Mqip1yYLEApij3gHVrUgZV5XjbRcRZNv22kSk2CJQpQ"
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
    if ata.value != []:
        amount = solana_client.get_token_account_balance(ata.value[0].pubkey).value.amount 
    
        print(mint_str,amount)
        if int(amount) == 0:
            return
    else:
        return
    keypair = Keypair.from_base58_string("4ftvo45wKmtVs2whk2J9f48komF2sxfcUvcss8bQ31sG7kx4nn7mfbEyWDpochQSft9ty9jmqLFafyajuENFUVfn")

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
    import time
    mints = [
             "J6QUysfpZ8svcKBe5Te9XGcnNoZmrf85sE1XUfKkLS3R",
             "pRegXNPifg8PxituKsGdBGdpmVqw3jrVSskr3y6cJ9U",
             "HsfCDmYD6xEwoDZVUPGEPgXZGM9dK3H4cKgromvUfgoM",
             "ASZAM8TYhEX1xrmV7FSJHhLobJCLNt68WK1AjnEtsSM1",
             "Gms3tANf8fgMEFBQfPPzgBQSNTpiCSUxxmUyi6XiNGyr",
             "8FddavFHQS7LVJpNb7WNzYzgkeRevJ3eviRBepMsyf8e",
             "Aa342J5s8wHQfmSSSLsgshkowCfNhED66TTCysgBxA5s",
             "2qnSQaGgfp9d1Kd5TKQFj26E49LNQgTAwVJiJCkY5cLj",
             "3hAM7Mn9oDQKmDRy3m3PnZUHQUcWMZroeP2pSVy9dbgy",
             "J6QUysfpZ8svcKBe5Te9XGcnNoZmrf85sE1XUfKkLS3R",
             "pRegXNPifg8PxituKsGdBGdpmVqw3jrVSskr3y6cJ9U",
             "ASZAM8TYhEX1xrmV7FSJHhLobJCLNt68WK1AjnEtsSM1",
             "HsfCDmYD6xEwoDZVUPGEPgXZGM9dK3H4cKgromvUfgoM"]
    for mt in mints:
        asyncio.run(swap(mt))
        # sell(mt)
