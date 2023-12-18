import asyncdb
from dao.models import CdaAddressReport


async def inserts_cda_address_report(cda_address_report: list[CdaAddressReport]) -> CdaAddressReport:
    return await asyncdb.inserts(cda_address_report, CdaAddressReport.table_name())
