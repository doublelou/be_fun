import requests
from tabulate import tabulate
import concurrent.futures

# Global variables for storing previous values
prev_market_cap_per_holder = {}
prev_holder_count = {}

def calculate_market_cap_per_holder(address, symbol):
    global prev_market_cap_per_holder, prev_holder_count
    
    url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{address}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 0:
            token_data = data["data"]["token"]
            market_cap = token_data["market_cap"]
            holder_count = token_data["holder_count"]
            
            if holder_count == 0:
                print(f"Holder count is zero for token {symbol}, cannot calculate.")
                return None, None, None, None
            
            market_cap_per_holder = market_cap / 100 / holder_count
            pool_info = token_data.get("pool_info", {})
            initial_quote_reserve = pool_info.get("initial_quote_reserve", None)
            rug_ratio = token_data.get("rug_ratio", None)
            
            # Check if previous values exist
            if symbol in prev_market_cap_per_holder:
                # Compare with previous value and set arrow
                if market_cap_per_holder > prev_market_cap_per_holder[symbol]:
                    market_cap_arrow = "↑"
                elif market_cap_per_holder < prev_market_cap_per_holder[symbol]:
                    market_cap_arrow = "↓"
                else:
                    market_cap_arrow = ""
            else:
                market_cap_arrow = ""

            if symbol in prev_holder_count:
                if holder_count > prev_holder_count[symbol]:
                    holder_count_arrow = "↑"
                elif holder_count < prev_holder_count[symbol]:
                    holder_count_arrow = "↓"
                else:
                    holder_count_arrow = ""
            else:
                holder_count_arrow = ""

            # Update previous values
            prev_market_cap_per_holder[symbol] = market_cap_per_holder
            prev_holder_count[symbol] = holder_count

            return market_cap_per_holder, initial_quote_reserve, rug_ratio, holder_count, market_cap_arrow, holder_count_arrow
        else:
            print(f"Failed to fetch data for token {symbol}.")
            return None, None, None, None, None, None
    except Exception as e:
        print(f"Error fetching data for token {symbol}: {str(e)}")
        return None, None, None, None, None, None

url = "https://gmgn.ai/defi/quotation/v1/wallet/sol/holdings/9M914xMEAud8v7zfB283MXCfa9p4Rwo4aPTjzCpNAnpf?orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true&limit=5000&tx30d=true"

try:
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and data.get("code") == 0:
        holdings = data["data"]["holdings"]
        filtered_holdings = [holding for holding in holdings if holding.get("total_profit_pnl") is not None and holding["total_profit_pnl"] > 3 and not holding.get("is_show_alert", True)]
        
        # Function to fetch data for a holding
        def process_holding(holding):
            address = holding["address"]
            symbol = holding["symbol"]
            total_profit_pnl = holding["total_profit_pnl"]
            market_cap_per_holder, initial_quote_reserve, rug_ratio, holder_count, market_cap_arrow, holder_count_arrow = calculate_market_cap_per_holder(address, symbol)
            if market_cap_per_holder is not None and holder_count > 300:
                return [address, symbol, total_profit_pnl, market_cap_per_holder, initial_quote_reserve if initial_quote_reserve is not None else 'None', rug_ratio if rug_ratio is not None else 'None', holder_count, market_cap_arrow, holder_count_arrow]
            else:
                return None
        
        # Concurrently process holdings
        with concurrent.futures.ThreadPoolExecutor() as executor:
            table_data = list(executor.map(process_holding, filtered_holdings))
            table_data = [data for data in table_data if data is not None]  # Remove None results
        
        # Sort table data by Total Profit PNL
        table_data.sort(key=lambda x: x[2])  # Sorting based on Total Profit PNL
        
        # Table headers
        table_headers = ["Address", "Symbol", "Total Profit PNL", "Market Cap per Holder", "Initial Quote Reserve", "Rug Ratio", "Holder Count", "Market Cap Change", "Holder Count Change"]
        
        # Print table
        print(tabulate(table_data, headers=table_headers))
    else:
        print("Failed to fetch data:", data.get("msg", "Unknown error"))
except Exception as e:
    print("Error:", str(e))
