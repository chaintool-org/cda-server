import csv
import json
import os
import time
from datetime import datetime
from typing import List
import pandas

from cffi.backend_ctypes import long
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from asyncdb import transaction
from dao import cda_user_dao, cda_address_operation_dao, cda_address_report_dao, cda_network_dao, user_api_token_dao
from dao.cda_user_dao import get_cda_user_by_id
from dao.models import CdaUser, CdaAddressOperation, CdaAddressReport, UserApiToken
from framework import errorcode
from framework.error_message import USER_NOT_FOUND, TEST_MODE_NOT_FOUND, NETWORK_NOT_FOUND, PUBLIC_NOT_FOUND, \
    CDA_ID_NOT_FOUND, START_TIME_ERROR, START_TIME_LENGTH_ERROR, END_TIME_ERROR, END_TIME_LENGTH_ERROR, PAGE_TYPE_ERROR, \
    PAGE_LENGTH_ERROR, OPERATE_ID_NOT_FOUND, TG_ID_NOT_FOUND
from framework.exceptions import BusinessException
from models.report_address_model import InputModel, DataEntry, DownloadModel

from framework.result_enc import suc_enc
from utils import constants, https_util, file_util, parameter_check, lark_notice_util
from utils.constants import test_mode, send_message_token, CONNECT_TYPE_TELEGRAM
from utils.date_util import validate_datetime_format, validate_time_range
from utils.file_util import get_json_data
from utils.login_checker import check_login
from utils.parameter_check import validate_param_in_list
import io

router = APIRouter()

# networks_file = "static/json/networks.json"
categories_file = "static/json/categories.json"
telegram_message_file = "static/html/telegram_message.html"

# networks = get_json_data(networks_file)
categories = get_json_data(categories_file)
telegram_message = file_util.get_file(telegram_message_file)


@router.get("/address/config")
async def get_config():
    networks = await cda_network_dao.get_all_valid_networks()
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
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, USER_NOT_FOUND)
    parameter_check.user_status_check(cda_user, False)

    if not validate_param_in_list(json_data.testMode, test_mode):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, TEST_MODE_NOT_FOUND)

    networks = await cda_network_dao.get_all_valid_networks()
    # 判断network是否在networks中
    for item in json_data.data:
        if not validate_param_in_list(item.network, networks):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, NETWORK_NOT_FOUND)

        if not validate_param_in_list(item.public, [0, 1]):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, PUBLIC_NOT_FOUND)

    operation_data = make_cda_address_operation_data(cda_user, json_data.json())
    last_inserted_id = await cda_address_operation_dao.save_cda_address_operation(operation_data)

    await cda_address_report_dao.inserts_cda_address_report(
        make_cda_address_report_data(json_data.data, last_inserted_id, cda_user.organization, json_data.testMode))

    char_member_result = https_util.get_telegram_chat_member(send_message_token[json_data.testMode]["token"],
                                                             send_message_token[json_data.testMode]["chat_id"],
                                                             cda_user.connect_id)
    tg_user_name = ""
    if char_member_result is not None:
        if char_member_result['result'] is not None and char_member_result['result']['user'] is not None and \
                char_member_result['result']['user']['username'] is not None:
            tg_user_name = char_member_result['result']['user']['username']

    if len(tg_user_name) == 0:
        await lark_notice_util.make_error_notice("获取不到tg用户名字的数据" + json.dumps(char_member_result))

    message = replace_placeholders(telegram_message, json_data.data[0],
                                   cda_user.id, cda_user.organization,
                                   cda_user.nickname, tg_user_name)

    result = https_util.send_telegram_message(send_message_token[json_data.testMode]["token"],
                                              send_message_token[json_data.testMode]["chat_id"], message)
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
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, CDA_ID_NOT_FOUND)

    if testMode is None:
        testMode = test_mode[2]
    else:
        if not validate_param_in_list(testMode, test_mode):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, TEST_MODE_NOT_FOUND)

    if startTime is not None:
        if startTime.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, START_TIME_ERROR)
        if len(startTime) != 13:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, START_TIME_LENGTH_ERROR)
    else:
        startTime = 0000000000000
    if endTime is not None:
        if endTime.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, END_TIME_ERROR)
        if len(endTime) != 13:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, END_TIME_LENGTH_ERROR)
    else:
        endTime = int(time.time()) * 1000

    if testMode is not None:
        if testMode.strip() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, TEST_MODE_NOT_FOUND)
    else:
        testMode = test_mode[2]
    if page is not None and page.isdigit() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, PAGE_TYPE_ERROR)
    else:
        page = 1
    if size is not None:
        if size.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, PAGE_LENGTH_ERROR)
    else:
        size = 20

    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_id(constants.CONNECT_TYPE_TELEGRAM, cdaId)

    # 判断cda_user为空时抛出异常
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, USER_NOT_FOUND)
    parameter_check.user_status_check(cda_user, False)

    addresses = []
    if operateId is not None:
        # 判断是否是纯数字
        if operateId.isdigit() is False:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, OPERATE_ID_NOT_FOUND)
        await cda_address_operation_dao.save_cda_address_operation(
            make_cda_address_operation_data(cda_user, json.dumps({
                "cda_id": cdaId,
                "operate_id": operateId
            }), 'QUERY'))
        cda_address_operation = await cda_address_operation_dao.get_cda_address_operation_by_id(int(operateId))
        if cda_address_operation is None:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, OPERATE_ID_NOT_FOUND)

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
                                    action_type: str = 'UPLOAD', data_count: int = 0):
    cda_address_operation = CdaAddressOperation()
    cda_address_operation.gmt_create = datetime.now()
    cda_address_operation.gmt_modified = datetime.now()
    cda_address_operation.cda_id = cda_user.id
    cda_address_operation.nickname = cda_user.nickname
    cda_address_operation.organization = cda_user.organization
    cda_address_operation.action_type = action_type
    cda_address_operation.data = data
    cda_address_operation.data_count = data_count
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
                         tg_user_nick_name: str):
    # 替换占位符
    html_content = html_template.format(
        nickname=tg_user_nick_name,
        reporter=nick_name,
        reporter_org=organization,
        id=operation_id,
        network=data.network,
        category=data.category,
        confidence=data.confidence,
        public='No' if data.public == 0 else 'Yes',
        source=data.source,
        entity=data.entity,
        addresses="\n".join([f'{i}. <code>{address}</code>' for i, address in enumerate(data.addresses, start=1)]),
    )
    return html_content


@router.get("/address/download")
async def download_csv(startDt: str, endDt: str, testMode: str = None, tgId: str = None):
    if tgId is None or tgId.strip() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, TG_ID_NOT_FOUND)
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)
    if not cda_user:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, USER_NOT_FOUND)

    if testMode is None:
        testMode = 'prod'
    df, headers = await get_download_data(cda_user, startDt, endDt, testMode)
    return Response(df.to_csv(), headers=headers, media_type="text/csv")


@router.post("/api/address/download")
@check_login()
async def api_download_csv(request: Request, download_param: DownloadModel):
    token = request.headers['TOKEN']
    start_result = await validate_datetime_format(download_param.startDt)
    end_result = await validate_datetime_format(download_param.endDt)
    if start_result is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "startDt format error")
    if end_result is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "endDt format error")
    if await validate_time_range(download_param.startDt, download_param.endDt) is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "startDt must be less than endDt")
    # 根据token获取对应对应的用户id
    user_api_token: UserApiToken = await user_api_token_dao.get_by_token(token)
    # 通过用户id获取用户信息
    user_info = await get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, user_api_token.user_id)
    if not user_info:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, USER_NOT_FOUND)
    # 用户装填检测
    if True is parameter_check.user_status_check(user_info):
        df, headers = await get_download_data(user_info, download_param.startDt, download_param.endDt)
        return Response(df.to_csv(), headers=headers, media_type="text/csv")


async def parse_none_value(param: str):
    if param is None or len(param) == 0 or param.isspace():
        return 'None'
    return param


async def get_download_data(user_info: CdaUser, start_dt: str, end_dt: str, test_mode: str = 'prod'):
    data = await cda_address_report_dao.get_report_list_by_dt(start_dt, end_dt, test_mode)
    rows = []
    for row in data:
        row_d = {'timestamp': row.get('timestamp'), 'record_id': row.get('record_id'),
                 'address': row.get('address'),
                 'network': await parse_none_value(row.get('network')),
                 'source': await parse_none_value(row.get('source')),
                 'confidence': await parse_none_value(row.get('confidence')),
                 'category': await parse_none_value(row.get('category')),
                 'entity': await parse_none_value(row.get('entity')),
                 'provider_org': await parse_none_value(row.get('provider_org')),
                 'public': row.get('public') > 0 if 'TRUE' else 'FALSE',
                 'nickname': row.get('nickname')
                 }
        rows.append(row_d)
    df = pandas.DataFrame(rows)
    headers = {'Content-Disposition': 'attachment; filename="data.csv"'}

    await cda_address_operation_dao.save_cda_address_operation(
        make_cda_address_operation_data(user_info, json.dumps({
            "cda_id": user_info.id,
            "startDt": start_dt,
            "endDt": end_dt
        }), action_type='DOWNLOAD', data_count=len(data)))
    return df, headers
