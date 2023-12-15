from asyncdb import get_list, sql_to_dict
from dao.models import CdaOrganization


async def get_all_valid_organizations():
    list = await sql_to_dict('select organization from cda_organization where status=0 order by id asc')
    relist = []
    for o in list:
        org = o.get("organization")
        relist.append(org)
    return relist
