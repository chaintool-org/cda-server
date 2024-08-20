from typing import List, Optional, Type

from pydantic import BaseModel, validator

from utils.parameter_check import validate_field_str, validate_field_list, validate_field_int


class OrgEntity(BaseModel):
    # 必填
    user_name: Optional[str]
    # 必填
    org: Optional[str]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

    @validator("org", pre=True, always=True)
    def validate_org_non_empty(cls, value):
        return validate_field_str(value, "org")


class NetworkEntity(BaseModel):
    # 必填
    user_name: Optional[str]
    # 必填
    network: Optional[str]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

    @validator("network", pre=True, always=True)
    def validate_network_non_empty(cls, value):
        return validate_field_str(value, "network")


class DownloadEntity(BaseModel):
    # 必填
    user_name: Optional[str]

    # 选填
    nickname: Optional[str]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")
