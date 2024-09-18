import os

import requests

from utils import lark_notice_util

tg_api_url = f"https://api.telegram.org/bot"


def send_telegram_message(bot_token, chat_id, message_text):
    api_url = f"{tg_api_url}{bot_token}/sendMessage"

    # 构建请求体
    request_data = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "pin_message": "true",
        "link_preview_options": '{"is_disabled":true}'
    }

    # 构建请求
    response = requests.post(api_url, data=request_data, timeout=600)

    # 检查响应状态码
    if response.status_code == 200:
        # 如果响应内容是JSON格式，可以使用 response.json() 来获取
        return response.json()
    elif response.status_code == 429:
        lark_notice_util.make_error_notice("Telegram API请求频率过高")
    else:
        print(f"HTTP请求失败，状态码：{response.status_code}")
        return None


def get_telegram_chat_member(bot_token, chat_id, user_id):
    api_url = f"{tg_api_url}{bot_token}/getChatMember"

    # 构建请求体
    request_data = {
        "chat_id": chat_id,
        "user_id": user_id,
    }

    # 构建请求
    response = requests.post(api_url, data=request_data, timeout=600)

    # 检查响应状态码
    if response.status_code == 200:
        print("获取跟用户聊天的用户信息", response.json())
        # 如果响应内容是JSON格式，可以使用 response.json() 来获取
        return response.json()
    elif response.status_code == 429:
        lark_notice_util.make_error_notice("Telegram API请求频率过高")
    else:
        print(f"HTTP请求失败，状态码：{response.status_code}")
        return None


async def send_file_via_api(bot_token, chat_id, message_id, file_path):
    url = f'{tg_api_url}{bot_token}/sendDocument'

    # 准备发送文件的数据
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': chat_id,
                'reply_to_message_id': message_id}

        try:
            # 发送请求
            response = requests.post(url, data=data, files=files)

            # 检查请求是否成功
            if response.status_code == 200:
                print('File sent successfully')
                # os.remove(file_path)
            else:
                print(f"Failed to send file: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error occurred: {e}")


async def set_commands(bot_token):
    # 设置机器人命令的 URL
    command_url = f"{tg_api_url}{bot_token}/setMyCommands"

    # 定义命令列表
    commands = [
        {"command": "report", "description": "Report risk data"},
        {"command": "download", "description": "Download risk data"}
    ]

    # 发送 POST 请求设置命令
    response = requests.post(command_url, json={"commands": commands})
    if response.status_code == 200:
        print("Bot commands set successfully.")
    else:
        print("Failed to set bot commands:", response.text)


async def set_webhook(bot_token, webhook_url):
    url = f"{tg_api_url}{bot_token}/setWebhook"
    response = requests.post(url, json={'url': webhook_url})
    if response.status_code == 200:
        print("Webhook set successfully.")
    else:
        print("Failed to set webhook:", response.text)


async def send_message_reply_message(bot_token, chat_id, message_id):
    # API URL
    url = f"{tg_api_url}{bot_token}/sendMessage"

    # 配置请求参数
    params = {
        'chat_id': chat_id,  # 对话ID
        'text': 'Click the button below to submit the risk data.',  # 消息文本
        'reply_to_message_id': message_id,  # 引用的消息ID
        'reply_markup': {
            'inline_keyboard': [
                [{'text': 'Report', 'url': 'https://t.me/CDAReporterBot/webapp?startapp=path_report__tokenType_prod'}]
            ]
        }
    }

    # 发送 POST 请求
    response = requests.post(url, json=params)

    # 检查响应结果
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Response: {response.text}")


async def download_reply_message(bot_token, chat_id, message_id, message):
    # API URL
    url = f"{tg_api_url}{bot_token}/sendMessage"

    # 配置请求参数
    params = {
        'chat_id': chat_id,  # 对话ID
        'text': message,
        # 消息文本
        'reply_to_message_id': message_id,  # 引用的消息ID
        "parse_mode": "HTML"
    }

    # 发送 POST 请求
    response = requests.post(url, json=params)

    # 检查响应结果
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Response: {response.text}")
