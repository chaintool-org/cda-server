from framework import errorcode
from framework.exceptions import BusinessException


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
