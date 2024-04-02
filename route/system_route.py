from fastapi import APIRouter

from asyncdb import transaction
from dao import cda_organization_dao, org_change_history, cda_network_dao, network_change_history
from framework.exceptions import BusinessException
from framework.result_enc import suc_enc
from models.system_change_model import OrgEntity, NetworkEntity

router = APIRouter()


@router.post("/org/add")
@transaction
async def add_org(data: OrgEntity):
    cda_organization = await cda_organization_dao.lock_organizations(data.org)
    if cda_organization is not None:
        raise BusinessException("The organization already exists")
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
        raise BusinessException("This organization does not exist")
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
        raise BusinessException("The network already exists")
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
        raise BusinessException("This network does not exist")
    # 添加操作记录
    await network_change_history.add_history(data, 1)
    # 删除network
    await cda_network_dao.delete_network(data.network)

    return suc_enc({
        'data': "删除成功👌"
    })

