from fastapi import APIRouter, Request

from dao.cda_organization_dao import get_all_valid_organizations
from dao.models import CdaUser
from framework.exceptions import BusinessException
from framework import errorcode
from dao import cda_user_dao
from framework.result_enc import suc_enc
from utils import constants

router = APIRouter()


@router.get("/user/tg/get_id")
async def get_cda_by_tg_id(telegramId: str = None):
    if telegramId is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')

    # 根据tgId查询用户
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, telegramId)

    if not cda_user:
        return suc_enc({
            'orgs': await get_all_valid_organizations()
        })

    return suc_enc({
        'cdaId': cda_user.id
    })


@router.post("/user/tg/connect")
async def connect_tg(telegramId: str = None, org: str = None, nickname: str = None):
    if telegramId is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')
    if org is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'org not present')

    ol = await get_all_valid_organizations()
    if org not in ol:
        raise BusinessException(errorcode.ORGANIZATION_NOT_EXIST, "organization not exist")

    # 判断tgid是否已存在
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, telegramId)

    if cda_user:
        return cda_user.id

    cda_user: CdaUser = CdaUser()
    cda_user.organization = org
    cda_user.connect_type = constants.CONNECT_TYPE_TELEGRAM
    cda_user.connect_id = telegramId
    cda_user.nickname = nickname
    await cda_user.save()

    saved_user = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, telegramId)

    return suc_enc({
        'cdaId': saved_user.id
    })
