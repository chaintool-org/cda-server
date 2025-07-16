from datetime import datetime
import json

from fastapi import APIRouter

from asyncdb import transaction
from dao import cda_address_report_dao, cda_organization_dao, org_change_history, cda_network_dao, network_change_history, \
    cda_address_operation_dao, cda_user_dao
from dao.models import CdaAddressOperation, CdaAddressReport
from dao.token_change_history import add_history
from dao.user_api_token_dao import get_by_user_id, save_token, update_status, update_token, list_user
from framework import errorcode
from framework.exceptions import BusinessException
from framework.result_enc import suc_enc
from models.system_change_model import AddressUploadBatchEntity, NetworkQueryEntity, OrgEntity, NetworkEntity, NameEntity, OrgQueryEntity, OrgUpdateEntity, UserAddEntity, UserQueryEntity, UserSaveEntity, \
    UserUpdateEntity, UserApiTokenEntity, UserTokenUpdateEntity, UserTokenResetEntity, UserUpdateInfoEntity
from route.address_route import make_cda_address_operation_data
from utils import parameter_check
from utils.constants import CONNECT_TYPE_TELEGRAM
from utils.parameter_check import validate_param_in_list


router = APIRouter()

@router.post("/org/add")
@transaction
async def add_org(data: OrgEntity):
    cda_organization = await cda_organization_dao.lock_organizations(data.org)
    if cda_organization is not None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "The organization already exists")
    # 添加操作记录
    await org_change_history.add_history(data, 0)
    # 添加org
    await cda_organization_dao.add_organization(data.org)

    return suc_enc({
        'data': "添加成功👌"
    })

@router.post("/org/list/valid")
async def get_valid_org_list():
    return suc_enc({'data': await cda_organization_dao.get_all_valid_organizations()})

@router.post("/org/list")
async def get_org_list(query: OrgQueryEntity):
    page = query.page if query.page is not None else 1
    page_size = query.page_size if query.page_size is not None else 20
    org_list_data = await cda_organization_dao.get_organization_list(query.name, query.status, page, page_size)
    total = org_list_data.get('total')
    data = org_list_data.get('data')
    page = org_list_data.get('page')
    page_size = org_list_data.get('page_size')
    return suc_enc({
        'data': data,
        'total': total,
        'page': page,
        'page_size': page_size
    })

@router.post("/org/update/{id}")
async def update_org(id: int, query: OrgUpdateEntity):
    await cda_organization_dao.update_organization(id, query.organization, query.status)
    return suc_enc({'data': "update success"})


@router.post("/org/delete")
@transaction
async def add_org(data: OrgEntity):
    cda_organization = await cda_organization_dao.lock_organizations(data.org)
    if cda_organization is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This organization does not exist")
    # 添加操作记录
    await org_change_history.add_history(data, 1)
    # 删除org
    await cda_organization_dao.delete_organizations(data.org)

    return suc_enc({'data': "delete success"})


@router.post("/network/list/valid")
async def get_network_list():
    network_list_data = await cda_network_dao.get_all_valid_networks()
    return suc_enc({'data': network_list_data})


@router.post("/network/list")
async def get_network_list(query: NetworkQueryEntity):
    page = query.page if query.page is not None else 1
    page_size = query.page_size if query.page_size is not None else 20
    network_list_data = await cda_network_dao.get_network_list(query.network, page, page_size)
    total = network_list_data.get('total')
    data = network_list_data.get('data')
    page = network_list_data.get('page')
    page_size = network_list_data.get('page_size')
    return suc_enc({
        'data': data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@router.post("/network/add")
@transaction
async def add_org(data: NetworkEntity):
    cda_network = await cda_network_dao.lock_network(data.network)
    if cda_network is not None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "The network already exists")
    # 添加操作记录
    await network_change_history.add_history(data, 0)
    # 添加network
    await cda_network_dao.add_network(data.network)
    return suc_enc({'data': "添加成功👌"})


@router.post("/network/delete/{id}")
@transaction
async def add_org(id: int, data: NetworkEntity):
    cda_network = await cda_network_dao.get_network_by_id(id)
    if cda_network is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This network does not exist")
    # 添加操作记录
    await network_change_history.add_history(data, 1)
    # 删除network
    await cda_network_dao.delete_network(cda_network)

    return suc_enc({'data': "删除成功"})

@router.post("/network/enable/{id}")
@transaction
async def enable_network(id: int, data: NetworkEntity):
    cda_network = await cda_network_dao.get_network_by_id(id)
    if cda_network is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This network does not exist")
    # 添加操作记录
    await network_change_history.add_history(data, 1)
    # 删除network
    await cda_network_dao.enable_network(cda_network)

    return suc_enc({'data': "启用成功"})


@router.post("/download/data/get")
async def get_download_data(query_data: NameEntity):
    # 返回得到的信息
    if query_data.nickname is None:
        cda_user_msg = await cda_address_operation_dao.query_operation()
    else:
        cda_user_msg = await cda_address_operation_dao.list_by_nickname(query_data.nickname)

    return suc_enc({
        'data': cda_user_msg
    })

@router.post("/address/report/batch")
async def upload_batch_address(query_data: AddressUploadBatchEntity):
    # check list network
    networks = await cda_network_dao.get_all_valid_networks()
    
    # check network list
    for item in query_data.data:
        if not validate_param_in_list(item.network, networks):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'network not found')
        
        if not validate_param_in_list(item.public, [0, 1]):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'public value is not valid')
        
        if not validate_param_in_list(item.confidence, ['High', 'Medium', 'Low']):
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'confidence value is not valid')
    
    # 构建cda_address_operation数据
    cda_address_operation = CdaAddressOperation()
    cda_address_operation.gmt_create = datetime.now()
    cda_address_operation.gmt_modified = datetime.now()
    cda_address_operation.nickname = query_data.user_name
    cda_address_operation.organization = 'SYSTEM'
    cda_address_operation.action_type = 'SYSTEM_MULTI_UPLOAD'
    cda_address_operation.data = json.dumps([item.dict() for item in query_data.data])
    cda_address_operation.data_count = len(query_data.data)
    last_inserted_id = await cda_address_operation_dao.save_cda_address_operation(cda_address_operation)


    address_report_list = []
    # 构建cda_address_report数据
    for item in query_data.data:
        cda_address_report = CdaAddressReport()
        cda_address_report.operate_id = last_inserted_id
        cda_address_report.address = item.address
        cda_address_report.network = item.network
        cda_address_report.category = item.category
        cda_address_report.confidence = item.confidence
        cda_address_report.source = item.source
        cda_address_report.entity = item.entity
        cda_address_report.is_public = item.public
        cda_address_report.mode = 'prod'
        cda_address_report.organization = 'SYSTEM'
        address_report_list.append(cda_address_report)

    await cda_address_report_dao.inserts_cda_address_report(address_report_list)

    return suc_enc({'data': "上传成功"})

@router.post("/user/list")
async def get_user_list(query: UserQueryEntity):
    user_list_data = await cda_user_dao.list_user(query.nickname, query.page, query.page_size)
    total = user_list_data.get('total')
    data = user_list_data.get('data')
    page = user_list_data.get('page')
    page_size = user_list_data.get('page_size')

    return suc_enc({
        'data': data,
        'total': total,
        'page': page,
        'page_size': page_size
    })

@router.post("/user/save")
@transaction
async def update_user(query_data: UserSaveEntity):
    already_data = []
    for data in query_data.data:
        cda_user = await cda_user_dao.get_cda_user_by_user_name(CONNECT_TYPE_TELEGRAM, data['nickname'])
        if cda_user is None:
            await cda_user_dao.save_user(data['connect_type'], data['nickname'], data['organization'])
        else:
            already_data.append(data['nickname'])
    return suc_enc({'data': already_data})


@router.post("/user/add")
@transaction
async def add_user(params: UserAddEntity):

    cda_user = await cda_user_dao.get_cda_user_by_user_name(CONNECT_TYPE_TELEGRAM, params.nickname)
    if cda_user is not None:
        raise BusinessException(errorcode.USER_HAS_BEEN_ADDED, "This user already exists")
    
    cda_user = await cda_user_dao.save_user(CONNECT_TYPE_TELEGRAM, params.nickname, params.organization)
    return suc_enc({'data': cda_user})

@router.post("/user/update/{user_id}")
async def update_user(user_id: int, query_data: UserUpdateInfoEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    await cda_user_dao.update_user_by_user_id(user_id, query_data.nickname, query_data.organization, query_data.status)
    return suc_enc({'data': "update success"})


@router.post("/user/update")
async def update_user(query_data: UserUpdateEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(query_data.user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    await cda_user_dao.update_status(query_data.user_id, query_data.status)
    return suc_enc({'data': "用户状态更新成功👌"})


@router.post("/user/token/list")
async def get_user_token_list(post_data: UserQueryEntity):
    return suc_enc({'data': await list_user()})


@router.post("/user/token/save")
async def save_user_token(post_data: UserApiTokenEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(post_data.user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    if True is parameter_check.user_status_check(cda_user):
        user_token_info = await get_by_user_id(post_data.user_id)
        if user_token_info:
            return suc_enc({'data': user_token_info['token'], "message": "该账户已存在token"})
        user_token = await save_token(post_data.user_id)
        await add_history(post_data.user_name, user_token, 0)
        return suc_enc({'data': user_token, "message": "添加成功"})


@router.post("/user/token/status/update")
async def update_user_token_status(post_data: UserTokenUpdateEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(post_data.user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    user_token_info = await get_by_user_id(post_data.user_id)
    if user_token_info is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user token does not exist")
    if True is parameter_check.user_status_check(cda_user):
        await update_status(post_data.user_id, post_data.status)
        await add_history(post_data.user_name, user_token_info['token'], 2 if post_data.status == 'EXPIRE' else 3)
    return suc_enc({"message": "状态修改成功"})


@router.post("/user/token/reset")
async def update_user_token_status(post_data: UserTokenResetEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(post_data.user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    if True is parameter_check.user_status_check(cda_user):
        token = await update_token(post_data.user_id)
        await add_history(post_data.user_name, token, 4)
        return suc_enc({"message": "重置token成功", "data": token})
