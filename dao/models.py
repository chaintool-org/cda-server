from asyncdb import *


class CdaUser(BaseDbModel):
    id = IntegerField(primary_key=True, auto_inc=True)
    gmt_create = DateTimeField(auto_now=True)
    gmt_modified = DateTimeField(auto_now=True)
    organization = CharField(max_length=32)
    connect_type = CharField(max_length=32)
    nickname = CharField(max_length=32)
    status = IntegerField()

    @classmethod
    def table_name(cls):
        return "cda_users"
