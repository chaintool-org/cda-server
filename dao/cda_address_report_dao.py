import asyncdb
from dao.models import CdaAddressReport


async def inserts_cda_address_report(cda_address_report: list[CdaAddressReport]) -> CdaAddressReport:
    return await asyncdb.inserts(cda_address_report, CdaAddressReport.table_name())


async def list_cda_address_report(ids: list[str], page: int, size: int) -> list[CdaAddressReport]:
    list = await asyncdb.sql_to_dict(
        f'select * from cda_address_report where operate_id in ({asyncdb.get_sql_params_content_by_list(ids)}) '
        f'order by gmt_create desc limit {size} offset {(page - 1) * size}',
        *ids
    )

    relist = []
    for item in list:
        relist.append(CdaAddressReport(**item))

    return relist
