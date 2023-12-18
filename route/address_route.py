from datetime import datetime

from fastapi import APIRouter, Request

from dao import cda_user_dao, cda_address_operation_dao, cda_address_report_dao
from dao.models import CdaUser, CdaAddressOperation, CdaAddressReport
from framework import errorcode
from framework.exceptions import BusinessException
from models.report_address_model import InputModel, DataEntry

from framework.result_enc import suc_enc
from utils import constants
from utils.file_util import get_json_data
from utils.paramer_check import validate_param_in_list

router = APIRouter()

networks_file = "static/networks.json"
categories_file = "static/categories.json"

networks = get_json_data(networks_file)
categories = get_json_data(categories_file)


@router.get("/address/config")
async def get_config():
    return suc_enc({
        "networks": networks,
        "categories": categories
    })


@router.post("/address/report")
async def report_address(json_data: InputModel):
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM,
                                                                        json_data.cdaId)
    # 判断cda_user为空时抛出异常
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'User does not exist!')

    # 判断network是否在networks中
    for item in json_data.data:
        if not validate_param_in_list(item.network, networks):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Network does not exist!')

        if not validate_param_in_list(item.category, categories):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Category does not exist!')

        if not validate_param_in_list(item.public, [0, 1]):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'Public does not exist!')

    operation_data = make_cda_address_operation_data(cda_user, json_data)
    last_inserted_id = await cda_address_operation_dao.save_cda_address_operation(operation_data)

    await cda_address_report_dao.inserts_cda_address_report(
        make_cda_address_report_data(json_data.data, last_inserted_id, cda_user.organization))

    return suc_enc({})


def make_cda_address_operation_data(cda_user: CdaUser, json_data: InputModel):
    cda_address_operation = CdaAddressOperation()
    cda_address_operation.gmt_create = datetime.now()
    cda_address_operation.gmt_modified = datetime.now()
    cda_address_operation.cda_id = cda_user.connect_id
    cda_address_operation.nickname = cda_user.nickname
    cda_address_operation.organization = cda_user.organization
    cda_address_operation.action_type = 'UPLOAD'
    cda_address_operation.data = json_data.json()
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
