import asyncdb
from asyncdb import get_list, sql_to_dict
from dao.models import CdaOrganization, CdaNetwork


async def get_all_valid_networks():
    list = await sql_to_dict(f'select network from {CdaNetwork.table_name()} where status=0 order by id asc')
    relist = []
    for o in list:
        org = o.get("network")
        relist.append(org)
    return relist


async def lock_network(network: str):
    return await CdaNetwork.single('network =%s for update', network)


async def add_network(network: str):
    cda_network = CdaNetwork()
    cda_network.network = network
    await cda_network.save()


async def delete_network(network: str):
    await asyncdb.delete(CdaNetwork.table_name(), "network = %s", network)
