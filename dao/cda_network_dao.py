import asyncio
import asyncdb
from asyncdb import get_list, sql_to_dict
from dao.models import CdaOrganization, CdaNetwork

async def paginated_query(model_class, filters=None, page=1, page_size=10, order_by="id asc"):
    page = max(page, 1)
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size
    
    if filters:
        conditions, params = zip(*filter(None, filters))
        where_clause = f" where {' and '.join(conditions)}" if conditions else ""

    table_name = model_class.table_name()

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


async def get_all_valid_networks():
    list = await sql_to_dict(f'select network from {CdaNetwork.table_name()} where status=0 order by id asc')
    relist = []
    for o in list:
        org = o.get("network")
        relist.append(org)
    return relist

async def get_network_list(network: str, page: int, page_size: int):
    filters = [
        ("network like %s", f"%{network}%") if network is not None else None,
    ]
    return await paginated_query(CdaNetwork, filters, page, page_size, "id desc")


async def lock_network(network: str):
    return await CdaNetwork.single('network =%s for update', network)


async def get_network_by_id(id: int):
    return await CdaNetwork.single('id = %s', id)


async def add_network(network: str):
    cda_network = CdaNetwork()
    cda_network.network = network
    await cda_network.save()


async def delete_network(network: CdaNetwork):
    network.status = 1
    await network.save()

async def enable_network(network: CdaNetwork):
    network.status = 0
    await network.save()


