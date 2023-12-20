import asyncdb
from asyncdb import sql_to_dict
from dao.models import CdaAddressOperation


async def save_cda_address_operation(cda_address_operation: CdaAddressOperation) -> str:
    return await CdaAddressOperation.save(cda_address_operation)


async def cda_address_operation_id(cda_id: str) -> list:
    list = await sql_to_dict('select id from cda_address_operation where cda_id = %s', cda_id)
    if len(list) == 0:
        return None
    relist = []
    for i in list:
        relist.append(i['id'])
    return relist


async def get_cda_address_operation_by_id(operation_id: str) -> CdaAddressOperation:
    print(operation_id)
    return await asyncdb.get_single(CdaAddressOperation.table_name(), 'id = %s', operation_id)
