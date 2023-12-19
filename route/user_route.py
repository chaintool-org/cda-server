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
async def get_cda_by_tg_id(tgId: str = None):
    if tgId is None or tgId == '':
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')

    # 根据tgId查询用户
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)

    if cda_user:
        if cda_user.status == 0:
            return suc_enc({
                'cdaId': cda_user.id
            })
        if cda_user.status == 1:
            raise BusinessException(errorcode.USER_HAS_BEEN_DELETED,
                                    'user has been deleted ,please contact administrator!')
        if cda_user.status == 2:
            raise BusinessException(errorcode.USER_HAS_BEEN_BANNED,
                                    'user has been banned ,please contact administrator!')

    if not cda_user:
        return suc_enc({
            'orgs': await get_all_valid_organizations()
        })


@router.post("/user/tg/connect")
async def connect_tg(tgId: str = None, org: str = None, nickname: str = None):
    if tgId is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')
    if org is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'org not present')
    if nickname is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'nickname not present')

    ol = await get_all_valid_organizations()
    if org not in ol:
        raise BusinessException(errorcode.ORGANIZATION_NOT_EXIST, "organization not exist")

    # 判断tgid是否已存在
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)

    if cda_user:
        if cda_user.status == 0:
            return suc_enc({
                'cdaId': cda_user.id
            })
        if cda_user.status == 1:
            raise BusinessException(errorcode.USER_HAS_BEEN_DELETED,
                                    'user has been deleted ,please contact administrator!')
        if cda_user.status == 2:
            raise BusinessException(errorcode.USER_HAS_BEEN_BANNED,
                                    'user has been banned ,please contact administrator!')

    cda_user: CdaUser = CdaUser()
    cda_user.organization = org
    cda_user.connect_type = constants.CONNECT_TYPE_TELEGRAM
    cda_user.connect_id = tgId
    cda_user.nickname = nickname
    await cda_user.save()

    saved_user = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)

    return suc_enc({
        'cdaId': saved_user.id
    })
