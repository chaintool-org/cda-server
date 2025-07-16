import asyncdb
from asyncdb import get_list, sql_to_dict, execute_sql
from dao.models import CdaOrganization
import asyncio

# 通用分页查询助手
async def paginated_query(model_class, filters=None, page=1, page_size=10, order_by="id asc"):
    """
    通用分页查询助手
    :param model_class: 模型类
    :param filters: 过滤条件列表 [("column like %s", value), ...]
    :param page: 页码
    :param page_size: 每页大小
    :param order_by: 排序字段
    """
    page = max(page, 1)
    page_size = max(page_size, 10)
    offset = (page - 1) * page_size
    
    # 构建查询条件
    if filters:
        conditions, params = zip(*filter(None, filters))
        where_clause = f" where {' and '.join(conditions)}" if conditions else ""
    else:
        where_clause, params = "", []
    
    table_name = model_class.table_name()
    
    # 并发执行查询
    data_result, count_result = await asyncio.gather(
        sql_to_dict(f"select * from {table_name}{where_clause} order by {order_by} limit %s offset %s", 
                   *params, page_size, offset),
        sql_to_dict(f"select count(*) as total from {table_name}{where_clause}", *params)
    )
    
    return {
        "data": model_class._change_list(data_result),
        "total": count_result[0]['total'] if count_result else 0,
        "page": page,
        "page_size": page_size
    }


async def get_all_valid_organizations():
    list = await sql_to_dict('select organization from cda_organization where status=0 order by id asc')
    relist = []
    for o in list:
        org = o.get("organization")
        relist.append(org)
    return relist


async def get_organization_list(name: str, status: int, page: int, page_size: int):
    filters = [
        ("organization like %s", f"%{name}%") if name is not None else None,
        ("status = %s", status) if status is not None else None
    ]
    return await paginated_query(CdaOrganization, filters, page, page_size)

async def lock_organizations(organization: str):
    return await CdaOrganization.single('organization =%s for update', organization)

async def add_organization(organization: str):
    cda_organization = CdaOrganization()
    cda_organization.organization = organization
    await cda_organization.save()

async def update_organization(id:int,  organization: str, status: int):
    sql = f'update {CdaOrganization.table_name()} set organization = %s, status = %s where id = %s'
    await execute_sql(sql, organization, status, id)

async def delete_organizations(organization: str):
    sql = f"update {CdaOrganization.table_name()} set status=1 where binary organization = %s"
    await sql_to_dict(sql, organization)
