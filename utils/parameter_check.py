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


def validate_input(input_str):
    # 正则表达式，匹配纯数字、纯字母或数字与字母的组合
    pattern = re.compile(r"^(?:(\d+)|([a-zA-Z]+)|(\d+[a-zA-Z]+|[a-zA-Z]+\d+))$")

    # 进行匹配
    match = pattern.match(input_str)

    if match:
        return True
    else:
        return False
