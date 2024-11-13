import logging
from datetime import datetime, timedelta
from functools import wraps

import requests
from starlette.requests import Request

from asyncdb import setting
from dao import user_api_token_dao
from framework import errorcode
from framework.exceptions import BusinessException
from utils import headers_util

logger = logging.getLogger(__name__)


def check_login(code_check=False):
    def decorator(target_function):
        @wraps(target_function)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')

            # if 'UID' not in request.headers:
            #     raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'missing header UID!')

            if 'Token' not in request.headers:
                raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, 'missing header Token!')

            token = headers_util.get_header(request, 'Token')
            await token_check(token)
            ret = await target_function(*args, **kwargs)
            return ret

        return wrapper

    return decorator


async def token_check(token):
    user_api_token = await user_api_token_dao.get_by_token(token)
    if user_api_token is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This token does not exist")
    if user_api_token.status == 'EXPIRE':
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "This token is disabled")
