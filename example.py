# from solders.keypair import Keypair
# from solanatracker import SolanaTracker
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

# async def swap():
#     keypair = Keypair.from_base58_string("")

#     solana_tracker = SolanaTracker(keypair, "https://rpc.solanatracker.io/public?advancedTx=true")

#     swap_response = await solana_tracker.get_swap_instructions(
#         "So11111111111111111111111111111111111111112",  # From Token
#         "9KVknx2DMebvVDN82NFBjQBVyPqqtBcbhABU824To5PY",  # To Token
#         0.0005,  # Amount to swap
#         10,  # Slippage
#         str(keypair.pubkey()),  # Payer public key
#         0.00005,  # Priority fee (Recommended while network is congested)
#         True,  # Force legacy transaction for Jupiter
#     )

#     txid = await solana_tracker.perform_swap(swap_response)

#     if not txid:
#         # Add retries / handle error as needed
#         raise Exception("Swap failed")

#     # Returns txid when the swap is successful or raises an exception if the swap fails
#     print("Transaction ID:", txid)
#     print("Transaction URL:", f"https://explorer.solana.com/tx/{txid}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(swap())

from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
solana_client = Client("https://api.mainnet-beta.solana.com")
owner = "8ZeubP1FD4ZunFYhyB6UWhQHVuGenVXpgBCPxLA8gkJa"
mint = "4j3AVXkUaeUNYgmBTx3JydoYa8R6xVhtc3bjT117RiV1"

ata = solana_client.get_token_accounts_by_owner(Pubkey.from_string(owner), TokenAccountOpts(mint=Pubkey.from_string(mint)))
print(ata)
if ata.value != []:
    amt = solana_client.get_token_account_balance(ata.value[0].pubkey).value.amount 

    print(amt)