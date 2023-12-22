import re

from framework import errorcode
from framework.exceptions import BusinessException
from framework.result_enc import suc_enc


def validate_field_str(value, field_name: str):
    print(f"type------{field_name}", type(value))
    if not value:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} is not present")

    if not isinstance(value, str):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} type mismatch")

    return value


def validate_field_int(value, field_name: str):
    print(f"type------{field_name}", type(value))
    if value is None:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} is not present")

    if not isinstance(value, int):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} type mismatch")

    return value


def validate_field_list(value, field_name: str):
    print(f"type------{field_name}", type(value))
    if not value:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} is not present")

    if not isinstance(value, list):
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} type mismatch")

    return value


def validate_param_in_list(value, data: list):
    return value in data


def user_status_check(cda_user, is_return: bool = True):
    if cda_user:
        if is_return:
            if cda_user.status == 0:
                return True
        if cda_user.status == 1:
            raise BusinessException(errorcode.USER_HAS_BEEN_DELETED,
                                    'user has been deleted ,please contact administrator!')
        if cda_user.status == 2:
            raise BusinessException(errorcode.USER_HAS_BEEN_BANNED,
                                    'user has been banned ,please contact administrator!')


def validata_check_param(value, field_name: str):
    if value is None or str(value).strip() is False:
        raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, f"{field_name} is not present")
    return value
