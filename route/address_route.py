import json
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Request

from asyncdb import transaction
from dao import cda_user_dao, cda_address_operation_dao, cda_address_report_dao
from dao.models import CdaUser, CdaAddressOperation, CdaAddressReport
from framework import errorcode
from framework.exceptions import BusinessException
from models.report_address_model import InputModel, DataEntry

from framework.result_enc import suc_enc
from utils import constants, https_util, file_util, parameter_check
from utils.file_util import get_json_data
from utils.parameter_check import validate_param_in_list

router = APIRouter()

networks_file = "static/json/networks.json"
categories_file = "static/json/categories.json"
telegram_message_file = "static/html/telegram_message.html"

networks = get_json_data(networks_file)
categories = get_json_data(categories_file)
telegram_message = file_util.get_file(telegram_message_file)

# 发消息的testMode
test_mode = json.loads(os.getenv('send.message.list', '["dev", "test", "prod"]'))
# 发送消息的token
send_message_token = json.loads(os.getenv('send.message.token',
                                          '{"dev": {"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ",'
                                          ' "chat_id": "-4099496644"},"test": {"token": '
                                          '"6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", '
                                          '"chat_id": "-4099496644"},"prod": '
                                          '{"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", '
                                          '"chat_id": "-4099496644"}}'))


@router.get("/address/config")
async def get_config():
    print(test_mode)
    print(send_message_token)
    return suc_enc({
        "networks": networks,
        "categories": categories
    })


@router.post("/address/report")
@transaction
async def report_address(json_data: InputModel):
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_id(constants.CONNECT_TYPE_TELEGRAM, str(json_data.cdaId))
    # 判断cda_user为空时抛出异常
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'User does not exist!')
    parameter_check.user_status_check(cda_user, False)

    if not validate_param_in_list(json_data.testMode, test_mode):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'testMode does not exist!')

    # 判断network是否在networks中
    for item in json_data.data:
        if not validate_param_in_list(item.network, networks):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Network does not exist!')

        if not validate_param_in_list(item.category, categories):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Category does not exist!')

        if not validate_param_in_list(item.public, [0, 1]):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Public does not exist!')

    operation_data = make_cda_address_operation_data(cda_user, json_data.json())
    last_inserted_id = await cda_address_operation_dao.save_cda_address_operation(operation_data)

    await cda_address_report_dao.inserts_cda_address_report(
        make_cda_address_report_data(json_data.data, last_inserted_id, cda_user.organization))

    message = replace_placeholders(telegram_message, json_data.data[0],
                                   cda_user.id, cda_user.organization,
                                   cda_user.nickname,
                                   f"https://www.baidu.com/{last_inserted_id}")
    result = https_util.send_telegram_message(send_message_token[json_data.testMode]["token"],
                                              send_message_token[json_data.testMode]["chat_id"],
                                              message)
    if result:
        print("成功发送消息：", result)
    else:
        print("发送消息失败")
    return suc_enc({})


@router.get("/address/query")
@transaction
async def address_get_id(cdaId: str = None, operateId: str = None, page: int = 1, size: int = 20):
    if cdaId is None or parameter_check.validate_input(cdaId) is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'cdaId does not exist!')

    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_id(constants.CONNECT_TYPE_TELEGRAM, cdaId)
    # 判断cda_user为空时抛出异常
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'User does not exist!')
    parameter_check.user_status_check(cda_user, False)

    addresses = []
    if operateId is not None:
        # 判断是否是纯数字
        if operateId.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'operateId does not exist!')
        await cda_address_operation_dao.save_cda_address_operation(
            make_cda_address_operation_data(cda_user, json.dumps({
                "cda_id": cdaId,
                "operate_id": operateId
            }), 'QUERY'))
        cda_address_operation = await cda_address_operation_dao.get_cda_address_operation_by_id(operateId)
        if cda_address_operation is None:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Operation does not exist!')

        addresses = await cda_address_report_dao.list_cda_address_report_by_operate_id(cda_address_operation.id, page,
                                                                                       size)

    else:
        data = await cda_address_operation_dao.cda_address_operation_id(cda_user.id)
        if data is None:
            return suc_enc({"addresses": addresses})

        addresses = await cda_address_report_dao.list_cda_address_report(data, page, size)

    return suc_enc({"addresses": addresses})


def make_cda_address_operation_data(cda_user: CdaUser, data,
                                    action_type: str = 'UPLOAD'):
    cda_address_operation = CdaAddressOperation()
    cda_address_operation.gmt_create = datetime.now()
    cda_address_operation.gmt_modified = datetime.now()
    cda_address_operation.cda_id = cda_user.id
    cda_address_operation.nickname = cda_user.nickname
    cda_address_operation.organization = cda_user.organization
    cda_address_operation.action_type = action_type
    cda_address_operation.data = data
    return cda_address_operation


def make_cda_address_report_data(data_entry: list[DataEntry], operation_id: str, organization: str):
    cda_address_list = []
    for item in data_entry:
        for address in item.addresses:
            cda_address_report = CdaAddressReport()
            cda_address_report.gmt_create = datetime.now()
            cda_address_report.gmt_modified = datetime.now()
            cda_address_report.organization = organization
            cda_address_report.operate_id = operation_id
            cda_address_report.network = item.network
            cda_address_report.category = item.category
            cda_address_report.confidence = item.confidence
            cda_address_report.source = item.source
            cda_address_report.entity = item.entity
            cda_address_report.is_public = item.public
            cda_address_report.address = address
            cda_address_list.append(cda_address_report)
    return cda_address_list


def replace_placeholders(html_template, data: DataEntry, operation_id: str, organization: str, nick_name: str,
                         detail_link: str):
    # 替换占位符
    html_content = html_template.format(
        reporter=nick_name,
        reporter_org=organization,
        id=operation_id,
        network=data.network,
        category=data.category,
        confidence=data.confidence,
        addresses="\n".join([f'{i}. <code>{address}</code>' for i, address in enumerate(data.addresses, start=1)]),
        detail_link=detail_link
    )
    return html_content
