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

async def update_user_by_user_id(user_id: int, nickname: str, organization: str, status: int):
    sql = (f'update {CdaUser.table_name()} set nickname = "{nickname}", organization = "{organization}", status = "{status}" where id = "{user_id}"')
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


async def list_user(user_name: str, page: int, page_size: int):
    # 限制最大页数
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    sqlOrder = 'order by gmt_create desc'
    sqlLimit = f'limit {page_size} offset {offset}'

    sql = f'select * from {CdaUser.table_name()}'
    
    # 构建WHERE条件（忽略大小写）
    where_clause = ""
    if user_name:
        # 使用字符串拼接避免百分号问题
        where_clause = ' where LOWER(nickname) like LOWER(%s)'
        like_param = f'%{user_name}%'
        sql += where_clause

    final_sql = f'{sql} {sqlOrder} {sqlLimit}'
    print(final_sql)
    
    # 分别处理有参数和无参数的情况
    if user_name:
        data = await sql_to_dict(final_sql, like_param)
    else:
        data = await sql_to_dict(final_sql)

    # 获取总页数（也要应用相同的过滤条件）
    total_sql = f'select count(*) as total from {CdaUser.table_name()}{where_clause}'
    if user_name:
        totalData = await sql_to_dict(total_sql, like_param)
    else:
        totalData = await sql_to_dict(total_sql)
    total = totalData[0]['total']

    return {
        'total': total,
        'data': data,
        'page': page,
        'page_size': page_size
    }
