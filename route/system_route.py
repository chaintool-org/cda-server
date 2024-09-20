import json

from fastapi import APIRouter

from asyncdb import transaction
from dao import cda_organization_dao, org_change_history, cda_network_dao, network_change_history, \
    cda_address_operation_dao, cda_user_dao
from framework import errorcode
from framework.exceptions import BusinessException
from framework.result_enc import suc_enc
from models.system_change_model import OrgEntity, NetworkEntity, NameEntity, UserQueryEntity, UserSaveEntity, \
    UserUpdateEntity
from utils.constants import CONNECT_TYPE_TELEGRAM

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

    return suc_enc({
        'data': "删除成功👌"
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
    return suc_enc({
        'data': "添加成功👌"
    })


@router.post("/network/delete")
@transaction
async def add_org(data: NetworkEntity):
    cda_network = await cda_network_dao.lock_network(data.network)
    if cda_network is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This network does not exist")
    # 添加操作记录
    await network_change_history.add_history(data, 1)
    # 删除network
    await cda_network_dao.delete_network(data.network)

    return suc_enc({
        'data': "删除成功👌"
    })


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


@router.post("/user/list")
async def get_user_list(query_data: UserQueryEntity):
    return suc_enc({
        'data': await cda_user_dao.list_user()
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


@router.post("/user/update")
async def update_user(query_data: UserUpdateEntity):
    cda_user = await cda_user_dao.get_cda_user_by_id(CONNECT_TYPE_TELEGRAM, str(query_data.user_id))
    if cda_user is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This user does not exist")
    await cda_user_dao.update_status(query_data.user_id, query_data.status)
    return suc_enc({'data': "用户状态更新成功👌"})
