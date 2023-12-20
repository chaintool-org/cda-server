from typing import List, Optional, Type

from pydantic import BaseModel, validator

from utils.parameter_check import validate_field_str, validate_field_list, validate_field_int


class DataEntry(BaseModel):

    # 必填
    network: Optional[str]
    # 必填
    category: Optional[str]
    confidence: Optional[str]
    source: Optional[str]
    entity: Optional[str]
    # 必填
    public: Optional[int]
    # 必填
    addresses: Optional[List[str]]

    @validator("network", pre=True, always=True)
    def validate_network_non_empty(cls, value):
        return validate_field_str(value, "network")

    @validator("category", pre=True, always=True)
    def validate_category_non_empty(cls, value):
        return validate_field_str(value, "category")

    @validator("public", pre=True, always=True)
    def validate_public_non_empty(cls, value):
        return validate_field_int(value, "public")

    @validator("addresses", pre=True, always=True)
    def validate_addresses_non_empty(cls, value):
        return validate_field_list(value, "addresses")


class InputModel(BaseModel):
    # 必填
    cdaId: Optional[int]
    testMode: Optional[str] = "test"
    # 必填
    data: Optional[List[DataEntry]]

    # cdaId类型对比
    @validator("cdaId", pre=True, always=True)
    def validate_cdaId(cls, value):
        return validate_field_int(value, "cdaId")

    # # data不能为空
    @validator("data", pre=True, always=True)
    def validate_data_non_empty(cls, value):
        return validate_field_list(value, "data")
