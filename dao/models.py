from asyncdb import *


class CdaUser(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    organization = CharField(max_length=32)
    connect_type = CharField(max_length=32)
    connect_id = CharField(max_length=32)
    nickname = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "cda_users"


class CdaOrganization(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    organization = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "cda_organization"


class CdaAddressOperation(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    cda_id = CharField(max_length=32)
    nickname = CharField(max_length=128)
    organization = CharField(max_length=128)
    action_type = CharField(max_length=128)
    data = JSONField()

    @classmethod
    def table_name(cls):
        return "cda_address_operation"


class CdaAddressReport(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    organization = CharField(max_length=128)
    operate_id = CharField(max_length=64)
    address = CharField(max_length=128)
    network = CharField(max_length=32)
    category = CharField(max_length=64)
    confidence = CharField(max_length=128)
    source = CharField(max_length=128)
    entity = CharField(max_length=128)
    is_public = IntegerField()
    mode = CharField(max_length=16)

    @classmethod
    def table_name(cls):
        return "cda_address_report"


class OrgChangeHistory(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    organization = CharField(max_length=32)
    lark_user_name = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "org_change_history"


class CdaNetwork(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    network = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "cda_network"


class NetworkChangeHistory(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    network = CharField(max_length=32)
    lark_user_name = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "network_change_history"


class UserApiToken(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    user_id = CharField(max_length=32)
    token = CharField(max_length=128)
    status = CharField(max_length=8)
    @classmethod
    def table_name(cls):
        return "user_api_token"
