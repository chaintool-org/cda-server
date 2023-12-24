import json
import os
import time
from datetime import datetime
from typing import List

from cffi.backend_ctypes import long
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
test_mode = json.loads(os.getenv('SEND_MESSAGE_LIST', '["dev", "test", "prod"]'))
# 发送消息的token
send_message_token = json.loads(os.getenv('SEND_MESSAGE_TOKEN',
                                          '{"dev": {"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ",'
                                          ' "chat_id": "-4099496644"},"test": {"token": '
                                          '"6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", '
                                          '"chat_id": "-4099496644"},"prod": '
                                          '{"token": "6472718374:AAEsaQ8pPinVDeR27S0a07G7XR03CYuCEio", '
                                          '"chat_id": "-4005964363"}}'))


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
    # # 判断cda_user为空时抛出异常
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'User does not exist!')
    parameter_check.user_status_check(cda_user, False)

    if not validate_param_in_list(json_data.testMode, test_mode):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'testMode does not exist!')

    # 判断network是否在networks中
    for item in json_data.data:
        if not validate_param_in_list(item.network, networks):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Network does not exist!')

        if not validate_param_in_list(item.public, [0, 1]):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Public does not exist!')

    operation_data = make_cda_address_operation_data(cda_user, json_data.json())
    last_inserted_id = await cda_address_operation_dao.save_cda_address_operation(operation_data)

    await cda_address_report_dao.inserts_cda_address_report(
        make_cda_address_report_data(json_data.data, last_inserted_id, cda_user.organization, json_data.testMode))

    message = replace_placeholders(telegram_message, json_data.data[0],
                                   cda_user.id, cda_user.organization,
                                   cda_user.nickname, json_data.source)

    result = https_util.send_telegram_message(send_message_token[json_data.testMode]["token"],
                                              send_message_token[json_data.testMode]["chat_id"])
    if result:
        print("成功发送消息：", result)
    else:
        print("发送消息失败")
    return suc_enc({})


@router.get("/address/query")
@transaction
async def address_get_id(cdaId: str = None, operateId: str = None, startTime: str = None, endTime: str = None,
                         testMode: str = None,
                         page: str = None, size: str = None):
    if cdaId is None or cdaId.strip() is False or cdaId.isdigit() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'cdaId does not exist!')

    if testMode is None:
        testMode = test_mode[2]
    else:
        if not validate_param_in_list(testMode, test_mode):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'testMode does not exist!')

    if startTime is not None:
        if startTime.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'startTime error!')
        if len(startTime) != 13:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'startTime length error!')
    else:
        startTime = 0000000000000
    if endTime is not None:
        if endTime.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'endTime error!')
        if len(endTime) != 13:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'endTime length error!')
    else:
        endTime = int(time.time()) * 1000

    if testMode is not None:
        if testMode.strip() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'testMode does not exist!')
    else:
        testMode = test_mode[2]
    if page is not None and page.isdigit() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'page Not a number!')
    else:
        page = 1
    if size is not None:
        if size.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'size Not a number!')
    else:
        size = 20

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
        cda_address_operation = await cda_address_operation_dao.get_cda_address_operation_by_id(int(operateId))
        if cda_address_operation is None:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Operation does not exist!')

        addresses = await cda_address_report_dao.get_prod_cda_address_report_by_id(operate_id=cda_address_operation.id,
                                                                                   page=int(page),
                                                                                   size=int(size),
                                                                                   mode=testMode,
                                                                                   start_time=int(startTime),
                                                                                   end_time=int(endTime))

    else:
        data = await cda_address_operation_dao.cda_address_operation_id(cda_user.id)
        if data is None:
            return suc_enc({"addresses": addresses})

        addresses = await cda_address_report_dao.get_prod_cda_address_report_by_id(ids=data,
                                                                                   page=int(page),
                                                                                   size=int(size),
                                                                                   mode=testMode,
                                                                                   start_time=int(startTime),
                                                                                   end_time=int(endTime))

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


def make_cda_address_report_data(data_entry: list[DataEntry], operation_id: str, organization: str, test_mode: str):
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
            cda_address_report.mode = test_mode
            cda_address_list.append(cda_address_report)
    return cda_address_list


def replace_placeholders(html_template, data: DataEntry, operation_id: str, organization: str, nick_name: str,
                         source: str):
    # 替换占位符
    html_content = html_template.format(
        reporter=nick_name,
        reporter_org=organization,
        id=operation_id,
        network=data.network,
        category=data.category,
        confidence=data.confidence,
        source=source,
        addresses="\n".join([f'{i}. <code>{address}</code>' for i, address in enumerate(data.addresses, start=1)]),
    )
    return html_content
