from asyncdb import sql_to_dict, execute_sql
from dao.models import UserApiToken, CdaUser
from utils.ids_util import generate_unique_id


async def get_by_user_id(user_id: str):
    sql = (f"SELECT * "
           f"FROM {UserApiToken.table_name()} "
           f"WHERE user_id = '{user_id}' "
           f"LIMIT 1")
    data = await sql_to_dict(sql)
    return data[0] if data else None


async def get_by_token(token: str):
    sql = (f"SELECT * "
           f"FROM {UserApiToken.table_name()} "
           f"WHERE token = '{token}' "
           f"LIMIT 1")
    data = await sql_to_dict(sql)
    return data[0] if data else None


async def update_status(user_id: str, status: str):
    sql = f'update {UserApiToken.table_name()} set status = "{status}" where user_id = "{user_id}"'
    await execute_sql(sql)


async def list_user():
    sql = (f'SELECT (SELECT nickname FROM {CdaUser.table_name()} WHERE id = uat.user_id) AS nickname,uat.* '
           f'FROM {UserApiToken.table_name()} uat')
    data = await sql_to_dict(sql)
    return data if data else None


async def save_token(user_id: str):
    user_api_token = UserApiToken()
    user_api_token.user_id = user_id
    user_api_token.token = generate_unique_id(user_id)
    await user_api_token.save()
    return user_api_token.token


async def update_token(user_id: str):
    user_api_token = generate_unique_id(user_id)
    sql = f'update {UserApiToken.table_name()} set token = "{user_api_token}" where user_id = "{user_id}"'
    await execute_sql(sql)
    return user_api_token
