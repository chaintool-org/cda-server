import asyncdb
from asyncdb import get_list, sql_to_dict
from dao.models import CdaOrganization


async def get_all_valid_organizations():
    list = await sql_to_dict('select organization from cda_organization where status=0 order by id asc')
    relist = []
    for o in list:
        org = o.get("organization")
        relist.append(org)
    return relist


async def lock_organizations(organization: str):
    return await CdaOrganization.single('organization =%s for update', organization)


async def add_organization(organization: str):
    cda_organization = CdaOrganization()
    cda_organization.organization = organization
    await cda_organization.save()


async def delete_organizations(organization: str):
    await asyncdb.delete(CdaOrganization.table_name(), "organization = %s", organization)
