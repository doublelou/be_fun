import websocket
import json

def on_message(ws, message):
    message_data = json.loads(message)
    # 检查消息类型是否是交易事件
    if message_data["method"] == "accountNotification":
        account_data = message_data["params"]["result"]["value"]["data"]["parsed"]
        # 检查是否是与目标账户相关的交易
        if "info" in account_data and account_data["info"]["tokenAmount"]:
            transaction_info = account_data["info"]
            print("Received Transaction:", transaction_info)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Closed Connection")

def on_open(ws):
    # 订阅与目标账户相关的交易事件
    ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "accountSubscribe", "params": ["YOUR_ACCOUNT_ADDRESS"]}))

# 替换为实际的账户地址
YOUR_ACCOUNT_ADDRESS = "HZoxemecYjge7b4fhPQw8KXA5zp7my13qeXVHyjQHD6T"

# 初始化 WebSocket 连接
ws = websocket.WebSocketApp("wss://api.mainnet-beta.solana.com/", 
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

# 启动 WebSocket 连接
ws.run_forever()
