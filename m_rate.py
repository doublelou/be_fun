import requests
from tabulate import tabulate
import time
from termcolor import colored  # Import colored from termcolor for colored output

# Variables to store previous values
prev_market_cap_per_holder = {}
prev_holder_count = {}

def get_base_token_info():
    url = "https://gmgn.ai/defi/quotation/v1/pairs/sol/new_pairs?limit=50&orderby=swaps_1h&direction=desc&filters[]=not_honeypot&filters[]=not_risk"

    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 0:
            pairs = data["data"]["pairs"]
            base_token_info_list = [{"symbol": pair["base_token_info"]["symbol"], "address": pair["base_token_info"]["address"]} for pair in pairs]
            return base_token_info_list
        else:
            return []
    except Exception as e:
        print(f"Error fetching base token info: {str(e)}")
        return []

def calculate_market_cap_per_holder(symbol, address):
    url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{address}"

    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 0:
            token_data = data["data"]["token"]
            market_cap = token_data.get("market_cap")
            holder_count = token_data.get("holder_count")
            if market_cap is None or holder_count is None or holder_count == 0:
                print(f"Invalid data for token {symbol}, cannot calculate.")
                return None, None, None, None, None, None
            market_cap_per_holder = market_cap / 100 / holder_count
            pool_info = token_data.get("pool_info", {})
            initial_quote_reserve = pool_info.get("initial_quote_reserve", None)
            rug_ratio = token_data.get("rug_ratio", None)

            # Check if previous values exist
            if symbol in prev_market_cap_per_holder:
                # Compare with previous value and print colored arrow
                if market_cap_per_holder > prev_market_cap_per_holder[symbol]:
                    market_cap_arrow = colored("↑", "green")
                elif market_cap_per_holder < prev_market_cap_per_holder[symbol]:
                    market_cap_arrow = colored("↓", "red")
                else:
                    market_cap_arrow = ""
            else:
                market_cap_arrow = ""

            if symbol in prev_holder_count:
                if holder_count > prev_holder_count[symbol]:
                    holder_count_arrow = colored(f"↑{holder_count - prev_holder_count[symbol]}", "green")
                elif holder_count < prev_holder_count[symbol]:
                    holder_count_arrow = colored(f"↓{prev_holder_count[symbol] - holder_count}", "red")
                else:
                    holder_count_arrow = ""
            else:
                holder_count_arrow = ""

            return market_cap_per_holder, initial_quote_reserve, rug_ratio, holder_count, market_cap_arrow, holder_count_arrow
        else:
            print(f"Failed to fetch data for token {symbol}.")
            return None, None, None, None, None, None
    except Exception as e:
        print(f"Error fetching data for token {symbol}: {str(e)}")
        return None, None, None, None, None, None

# 更新全局变量的函数
def update_previous_values(market_cap_per_holder, holder_count, symbol):
    global prev_market_cap_per_holder, prev_holder_count
    prev_market_cap_per_holder[symbol] = market_cap_per_holder
    prev_holder_count[symbol] = holder_count

while True:
    # 获取基础代币信息
    base_token_info_list = get_base_token_info()

    # 保存表头
    table_headers = ["Token Symbol", "Address", "Market Cap per Holder", "Initial Quote Reserve", "Rug Ratio", "Holder Count", "Market Cap Change", "Holder Count Change"]

    # 保存表格数据
    table_data = []

    # 计算市值/持有者数量的比率并添加到表格数据中（仅在小于1时添加）
    for token_info in base_token_info_list:
        symbol = token_info["symbol"]
        address = token_info["address"]
        market_cap_per_holder, initial_quote_reserve, rug_ratio, holder_count, market_cap_arrow, holder_count_arrow = calculate_market_cap_per_holder(symbol, address)
        if market_cap_per_holder is not None and holder_count is not None and holder_count >= 300:
            table_data.append([symbol, address, market_cap_per_holder, initial_quote_reserve if initial_quote_reserve is not None else 'None', rug_ratio if rug_ratio is not None else 'None', holder_count, market_cap_arrow, holder_count_arrow])
            update_previous_values(market_cap_per_holder, holder_count, symbol)  # 更新全局变量
    
    # 打印表格
    print(tabulate(table_data, headers=table_headers))
    
    # 等待 30 秒
    time.sleep(30)
