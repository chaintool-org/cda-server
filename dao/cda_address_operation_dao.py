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


async def get_cda_address_operation_by_id(operation_id: int) -> CdaAddressOperation:
    return await asyncdb.get_single(CdaAddressOperation.table_name(), 'id = %s', operation_id)


async def list_download_data_by_cad_id() -> list:
    return await sql_to_dict(
        'SELECT gmt_create,nickname,organization,data_count FROM cda_address_operation '
        'WHERE action_type =%s ORDER BY gmt_create',
        "DOWNLOAD")


async def list_download_data_by_nickname(nickname: str) -> list:
    return await sql_to_dict(
        'SELECT gmt_create,nickname,organization,data_count FROM cda_address_operation '
        'WHERE action_type =%s and nickname = %s ORDER BY gmt_create',
        "DOWNLOAD", nickname)
