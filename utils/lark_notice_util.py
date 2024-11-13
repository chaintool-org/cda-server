import json

import requests

from asyncdb import setting
from utils.file_util import get_json_data

lark_base_notice_file = "static/json/lark_base_notice.json"

lark_base_notice = get_json_data(lark_base_notice_file)


async def make_error_notice(message):
    environment = setting.environment
    if environment is None:
        environment = "dev"
    if environment != "dev":
        base_body = lark_base_notice['content']['post']['zh_cn']
        base_body['title'] = "cda API 错误通知"
        error_message = [[{"text": message, "tag": "text"}]]
        base_body['content'] = error_message
        await send_post_request(lark_base_notice,
                                "https://open.larksuite.com/open-apis/bot/v2/hook/aa022d36-c0b9-4b41-a198-33bab81a7d17")


async def send_post_request(json_data,
                            url="https://open.larksuite.com/open-apis/bot/v2/hook/173774da-f7e9-4699-b3aa-0e9c1ad62aef"):
    # 设置请求头，指定 Content-Type 为 application/json
    headers = {"Content-Type": "application/json"}

    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(json_data), headers=headers)

    print(response.text)
    if response.status_code == 200:
        print("POST 请求成功！")
        print("响应数据:", response.json())
    else:
        print(f"POST 请求失败，状态码: {response.status_code}")
