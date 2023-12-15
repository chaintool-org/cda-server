from fastapi import APIRouter, Request

from dao.models import CdaUser
from framework.exceptions import BusinessException
from framework import errorcode
from dao import cda_user_dao
from framework.result_enc import suc_enc
from utils import constants

router = APIRouter()


@router.get("/user/tg/get_id")
async def get_cda_by_tg_id(telegramId: str, request: Request):
    if telegramId is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'telegram id is not present')

    # 根据tgId查询用户
    cda_user: CdaUser = await cda_user_dao.get_cda_user_by_connect_info(constants.CONNECT_TYPE_TELEGRAM, telegramId)

    if not cda_user:
        return suc_enc({
            'orgs': constants.CDA_ORGANS
        })

    return suc_enc({
        'cdaId': cda_user.id
    })
