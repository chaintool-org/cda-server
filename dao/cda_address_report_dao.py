import datetime

from cffi.backend_ctypes import long

import asyncdb
from dao.models import CdaAddressReport
from models import report_address_DTO


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
        relist.append(report_address_DTO.map_cda_address_report_to_dto(CdaAddressReport(**item)))

    return relist


async def list_cda_address_report_by_operate_id(operate_id: str, page: int, size: int) -> list[CdaAddressReport]:
    list = await asyncdb.sql_to_dict(
        f'select * from cda_address_report where operate_id = "{operate_id}"'
        f'order by gmt_create desc limit {size} offset {(page - 1) * size}'
    )

    relist = []
    for item in list:
        relist.append(report_address_DTO.map_cda_address_report_to_dto(CdaAddressReport(**item)))

    return relist


async def get_test_cda_address_report_by_id(operate_id: str = None, ids: list[str] = None, mode: str = 'test',
                                            page: int = 1,
                                            size: int = 20) -> CdaAddressReport:
    list = await asyncdb.sql_to_dict(
        f'select * from cda_address_report '
        f'where operate_id = "{operate_id}" '
        f'or (operate_id is null and operate_id in ({asyncdb.get_sql_params_content_by_list(ids)})) '
        f'order by gmt_create desc limit {size} offset {(page - 1) * size}'
    )
    relist = []
    for item in list:
        relist.append(report_address_DTO.map_cda_address_report_to_dto(CdaAddressReport(**item)))

    return relist


async def get_prod_cda_address_report_by_id(operate_id: int = None, ids: list[str] = None, mode: str = 'prod',
                                            start_time: int = None, end_time: int = None, page: int = 1,
                                            size: int = 20) -> CdaAddressReport:
    start_sql = ''
    end_sql = ''
    operate_id_sql = ''
    ids_sql = ''
    mode_sql = ''
    if start_time is not None:
        start_sql = f'and gmt_create >= FROM_UNIXTIME({start_time // 1000})'
    if end_time is not None:
        end_sql = f'and gmt_create <= FROM_UNIXTIME({end_time // 1000})'
    if operate_id is not None:
        operate_id_sql = f'and operate_id = "{operate_id}"'
    if ids is not None:
        ids_sql = f'and operate_id in ({asyncdb.get_sql_params_content_by_list(ids)})'
    if mode.strip():
        mode_sql = f'mode = "{mode}"'

    if ids is not None:
        list = await asyncdb.sql_to_dict(
            f'select * from cda_address_report '
            f'where {mode_sql} '
            f'{ids_sql} '
            f'{start_sql} '
            f'{end_sql} '
            f'order by gmt_create desc limit {size} offset {(page - 1) * size}', *ids
        )
    else:
        list = await asyncdb.sql_to_dict(
            f'select * from cda_address_report '
            f'where {mode_sql} '
            f'{operate_id_sql} '
            f'{start_sql} '
            f'{end_sql} '
            f'order by gmt_create desc limit {size} offset {(page - 1) * size}'
        )
    relist = []
    for item in list:
        relist.append(report_address_DTO.map_cda_address_report_to_dto(CdaAddressReport(**item)))

    return relist


async def get_report_list_by_dt(start_dt: str, end_dt: str, test_mode: str):
    return await asyncdb.sql_to_dict(
        f'select a.gmt_create as timestamp ,a.id as record_id,a.network,a.source,a.confidence,a.address,a.category,a.entity,a.organization,'
        f'a.is_public as public,a.organization as provider_org, c.nickname as nickname '
        f'from cda_address_report as a left join cda_address_operation as b on a.operate_id = b.id left join cda_users as c on b.cda_id = c.id '
        f'where a.gmt_create >= %s and a.gmt_create <%s and mode = %s',
        start_dt, end_dt, test_mode)
