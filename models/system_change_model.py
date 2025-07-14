from typing import List, Optional, Type

from pydantic import BaseModel, validator

from framework import errorcode
from framework.exceptions import BusinessException
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
    

class OrgUpdateEntity(BaseModel):
    organization: Optional[str]
    status: Optional[int]   

    @validator("organization", pre=True, always=True)
    def validate_organization_non_empty(cls, value):
        return validate_field_str(value, "organization")
    

class OrgQueryEntity(BaseModel):
    name: Optional[str]
    status: Optional[int]
    page: Optional[int]
    page_size: Optional[int]


class NetworkQueryEntity(BaseModel):
    network: Optional[str]
    page: Optional[int]
    page_size: Optional[int]


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


class NameEntity(BaseModel):
    # 必填
    user_name: Optional[str]

    nickname: Optional[str]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")


class UserQueryEntity(BaseModel):
    user_name: Optional[str]
    page: Optional[int]
    page_size: Optional[int]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        if value is None or value == "":
            return None
        return validate_field_str(value, "user_name")
    
    @validator("page", pre=True, always=True)
    def validate_page_non_empty(cls, value):
        return validate_field_int(value, "page")
    
    @validator("page_size", pre=True, always=True)
    def validate_page_size_non_empty(cls, value):
        return validate_field_int(value, "page_size")


class UserSaveEntity(BaseModel):
    user_name: Optional[str]
    data: List[dict]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

    @validator("data", pre=True, always=True)
    def validate_data_non_empty(cls, value):
        return validate_field_list(value, "data")
    
class UserAddEntity(BaseModel):
    nickname: str
    organization: str

    @validator("nickname", pre=True, always=True)
    def validate_nickname_non_empty(cls, value):
        return validate_field_str(value, "nickname")

    # @validator("connect_type", pre=True, always=True)
    # def validate_connect_type_non_empty_str(cls, value):
    #     return validate_field_str(value, "data")
    
    @validator("organization", pre=True, always=True)
    def validate_organization_non_empty_str(cls, value):
        return validate_field_str(value, "data")
    

class UserUpdateInfoEntity(BaseModel):
    nickname: Optional[str]
    organization: Optional[str]
    status: Optional[int]

    @validator("nickname", pre=True, always=True)
    def validate_nickname_non_empty(cls, value):
        return validate_field_str(value, "nickname")

    @validator("organization", pre=True, always=True)
    def validate_organization_non_empty(cls, value):
        return validate_field_str(value, "organization")

    @validator("status", pre=True, always=True)
    def validate_status_non_empty(cls, value):
        verify_value = validate_field_int(value, "status")
        if verify_value in [0, 1, 2]:
            return verify_value
        else:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "status must be 0 or 1 or -1") 

class UserUpdateEntity(BaseModel):
    user_name: Optional[str]
    user_id: Optional[int]
    status: Optional[int]

    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

    @validator("user_id", pre=True, always=True)
    def validate_user_id_non_empty(cls, value):
        return validate_field_int(value, "user_id")

    @validator("status", pre=True, always=True)
    def validate_status_non_empty(cls, value):
        verify_value = validate_field_int(value, "status")
        if verify_value in [0, 1, 2]:
            return verify_value
        else:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "status must be 0 or 1 or -1")

class UserApiTokenEntity(BaseModel):
    user_id: Optional[str]
    user_name: Optional[str]

    @validator("user_id", pre=True, always=True)
    def validate_user_id_non_empty(cls, value):
        return validate_field_int(value, "user_id")
    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

class UserTokenUpdateEntity(BaseModel):
    user_id: Optional[str]
    status: Optional[str]
    user_name: Optional[str]

    @validator("user_id", pre=True, always=True)
    def validate_user_id_non_empty(cls, value):
        return validate_field_int(value, "user_id")
    @validator("status", pre=True, always=True)
    def validate_status_non_empty(cls, value):
        verify_value = validate_field_str(value, "status")
        if verify_value in ['ACTIVE','EXPIRE']:
            return verify_value
        else:
            raise BusinessException(errorcode.REQUEST_PARAM_ILLEGAL, "status must be ACTIVE or EXPIRE")
    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")

class UserTokenResetEntity(BaseModel):
    user_id: Optional[str]
    user_name: Optional[str]

    @validator("user_id", pre=True, always=True)
    def validate_user_id_non_empty(cls, value):
        return validate_field_int(value, "user_id")
    @validator("user_name", pre=True, always=True)
    def validate_user_name_non_empty(cls, value):
        return validate_field_str(value, "user_name")