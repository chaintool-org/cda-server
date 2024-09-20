from asyncdb import sql_to_dict, execute_sql
from dao.models import CdaUser


async def get_cda_user_by_connect_info(connect_type: str, connect_id: str) -> CdaUser:
    return await CdaUser.single('connect_type = %s and connect_id = %s', connect_type, connect_id)


async def get_cda_user_by_id(connect_type: str, user_id: str) -> CdaUser:
    return await CdaUser.single('connect_type = %s and id = %s', connect_type, user_id)


async def get_cda_user_by_user_name(connect_type: str, nickname: str) -> CdaUser:
    return await CdaUser.single('connect_type = %s and nickname = %s', connect_type, nickname)


async def update_user_by_username(nickname: str, connect_id: int, connect_type: str):
    sql = (f'update {CdaUser.table_name()} set connect_id = "{connect_id}" where nickname = "{nickname}" '
           f'and connect_type = "{connect_type}"')
    await execute_sql(sql)


async def save_user(connect_type: str, nickname: str, organization: str):
    cda_user = CdaUser()
    cda_user.nickname = nickname
    cda_user.organization = organization
    cda_user.connect_type = connect_type
    await cda_user.save()


async def update_status(user_id: int, status: int):
    sql = f'update {CdaUser.table_name()} set status = {status} where id = {user_id}'
    await execute_sql(sql)


async def list_user():
    sql = f'select * from {CdaUser.table_name()} order by gmt_create desc '
    return await sql_to_dict(sql)
