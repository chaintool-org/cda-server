import requests


def send_telegram_message(bot_token, chat_id, message_text):
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # 构建请求体
    request_data = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "pin_message": "true"
    }

    # 构建请求
    response = requests.post(api_url, data=request_data)

    # 检查响应状态码
    if response.status_code == 200:
        # 如果响应内容是JSON格式，可以使用 response.json() 来获取
        return response.json()
    else:
        print(f"HTTP请求失败，状态码：{response.status_code}")
        return None


def get_telegram_chat_member(bot_token, chat_id, user_id):
    api_url = f"https://api.telegram.org/bot{bot_token}/getChatMember"

    # 构建请求体
    request_data = {
        "chat_id": chat_id,
        "user_id": user_id,
    }

    # 构建请求
    response = requests.post(api_url, data=request_data)

    # 检查响应状态码
    if response.status_code == 200:
        # 如果响应内容是JSON格式，可以使用 response.json() 来获取
        return response.json()
    else:
        print(f"HTTP请求失败，状态码：{response.status_code}")
        return None
