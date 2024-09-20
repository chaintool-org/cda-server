from fastapi import APIRouter, Request

from dao.cda_organization_dao import get_all_valid_organizations
from dao.models import CdaUser
from framework.exceptions import BusinessException
from framework import errorcode
from dao import cda_user_dao
from framework.result_enc import suc_enc
from utils import constants, parameter_check

router = APIRouter()


@router.get("/user/tg/get_id")
async def get_cda_by_tg_id(tgId: str = None):
    if tgId is None or tgId.strip() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')

    # 根据tgId查询用户
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)
    if True is parameter_check.user_status_check(cda_user):
        return suc_enc({
            'cdaId': cda_user.id
        })
    if not cda_user:
        return suc_enc({
            'orgs': await get_all_valid_organizations()
        })


@router.post("/user/tg/connect")
async def connect_tg(tgId: str = None, org: str = None, nickname: str = None):
    if tgId is None or not tgId.strip():
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')
    if org is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'org not present')
    if nickname is None or not nickname.strip():
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'nickname not present')

    ol = await get_all_valid_organizations()
    if org not in ol:
        raise BusinessException(errorcode.ORGANIZATION_NOT_EXIST, "organization not exist")

    # 判断tgid是否已存在
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, tgId)

    if True is parameter_check.user_status_check(cda_user):
        return suc_enc({
            'cdaId': cda_user.id
        })
    raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL,
                            "To use the CDA TG bot, you must first be a member of the CDA TG channel. Please contact your administrator to be added to the channel.")
