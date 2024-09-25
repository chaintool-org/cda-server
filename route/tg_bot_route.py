import os

from fastapi import APIRouter
from starlette.requests import Request

from asyncdb import setting
from dao import cda_user_dao
from dao.models import CdaUser
from framework.error_message import DOWNLOAD_ERROR_MSG, DOWNLOAD_ERROR_MSG_INVALID_TIME, DOWNLOAD_ERROR_MSG_NOT_FOUND, \
    DOWNLOAD_ERROR_MSG_FAILED, TG_USER_NOT_REGISTERED, TG_USER_DELETED, TG_USER_BANNED
from route.address_route import send_message_token, download_csv
from utils import file_util, https_util, constants
from utils.date_util import get_time, str_time_format, format1, format2
from utils.https_util import set_commands, set_webhook, send_message_reply_message, download_reply_message

router = APIRouter()
telegram_message_file = "static/html/telegram_download_message.html"
telegram_message = file_util.get_file(telegram_message_file)


@router.post("/api/tg/robot/init")
async def init():
    await set_commands(get_tg_token())
    await set_webhook(get_tg_token(),
                      setting.webhook_url)
    return "ok"


@router.post("/api/tg/robot/webhook")
async def message_handler(request: Request):
    data = await request.json()
    print(str(data))
    if data is not None:
        message_id, chat_id, username, chat_type = await get_tg_info(data)
        if message_id is not None and chat_id is not None and username is not None:
            next_step = await verify_user(chat_id, message_id, username, chat_type)
            if next_step is False:
                return "ok"
            await make_tg_message(message_id, chat_id, chat_type, data)
    return "ok1"


# 下载文件的处理函数
async def download_handler(command_args, chat_id, message_id, tg_bot_name):
    # 如果命令后没有参数，给出帮助提示
    if '/download' == command_args or f'/download{tg_bot_name}' == command_args:
        await download_reply_message(get_tg_token(), chat_id, message_id, telegram_message)
        return
    # 先去掉命令前缀 '/download'
    command_parts = command_args.strip().split(' ', 1)
    command_args = command_parts[1].strip() if len(command_parts) > 1 else ""
    # 检查命令后是否包含 'd', 'w', 'm' 或日期范围 '-'
    if not any(char in command_args for char in 'dwm-'):
        return await download_reply_message(get_tg_token(), chat_id, message_id,
                                            DOWNLOAD_ERROR_MSG)
    # 将输入的参数分割
    args = command_args.strip().split(' ')
    arg1 = args[0]
    arg2 = args[1] if len(args) > 1 else None

    # 解析时间
    time_range = get_time(arg1, arg2)
    if time_range is None:
        return await download_reply_message(get_tg_token(), chat_id, message_id, DOWNLOAD_ERROR_MSG_INVALID_TIME)

    start_time, end_time, id_str = time_range

    try:
        # 模拟下载过程
        csv_content = await download_csv(start_time, end_time, tgId=str(chat_id))

        if not csv_content:
            return await download_reply_message(get_tg_token(), chat_id, message_id,
                                                DOWNLOAD_ERROR_MSG_NOT_FOUND)
        # 保存文件
        temp_file = f"{await str_time_format(start_time, format1, format2)}_{await str_time_format(end_time, format1, format2)}.csv"
        with open(temp_file, 'wb') as file:
            file.write(csv_content.body)

        # 调用函数发送文件
        await https_util.send_file_via_api(get_tg_token(), chat_id=chat_id,
                                           message_id=message_id, file_path=temp_file)
        os.remove(temp_file)
    except Exception as e:
        print(f"Error during download: {e}")
        return await download_reply_message(get_tg_token(), chat_id, message_id, DOWNLOAD_ERROR_MSG_FAILED)


async def verify_user(chat_id, message_id, username, chat_type):
    next_step = False
    cda_user_by_id: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM,
                                                                              chat_id)
    cda_user_by_name: CdaUser = await cda_user_dao.get_cda_user_by_user_name(constants.CONNECT_TYPE_TELEGRAM,
                                                                             username)
    if cda_user_by_id is None and cda_user_by_name is None:
        await download_reply_message(get_tg_token(), chat_id, message_id,
                                     TG_USER_NOT_REGISTERED, chat_type)
    if cda_user_by_id is not None:
        if cda_user_by_id.status == 1:
            await download_reply_message(get_tg_token(), chat_id, message_id,
                                         TG_USER_DELETED, chat_type)

        if cda_user_by_id.status == 2:
            await download_reply_message(get_tg_token(), chat_id, message_id,
                                         TG_USER_BANNED, chat_type)
        if cda_user_by_id.status == 0:
            next_step = True
    if cda_user_by_id is None and cda_user_by_name is not None:
        await cda_user_dao.update_user_by_username(username, chat_id, constants.CONNECT_TYPE_TELEGRAM)
        next_step = True

    return next_step


def get_tg_token():
    environment = setting.environment
    if environment is None:
        environment = "dev"
    return send_message_token[environment]["token"]


async def get_tg_info(data):
    message_id, chat_id, username, chat_type = None, None, None, None
    if "message" in data:
        if "message_id" in data["message"]:
            message_id = data['message']['message_id']
        if "chat" in data["message"]:
            chat_type = data['message']['chat']['type']
        if "from" in data["message"] and "username" in data["message"]["from"]:
            username = data['message']['from']['username']
            chat_id = data['message']['from']['id']
    return message_id, chat_id, username, chat_type


async def make_tg_message(message_id, chat_id, chat_type, data):
    tg_bot_name = send_message_token[setting.environment]["tg_name"]
    if message_id is not None and chat_id is not None:
        if chat_type == 'group':
            return "非机器人私聊"
        if "text" not in data["message"]:
            return "no ok,没有text"
        text = data['message']['text']
        if text == '/report' == text or f'/report{tg_bot_name}' == text:
            await send_message_reply_message(get_tg_token(), chat_id,
                                             message_id)
        if '/download' in text or f'/download{tg_bot_name}' == text:
            await download_handler(text, chat_id,
                                   message_id, tg_bot_name)
