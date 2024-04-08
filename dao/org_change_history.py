from dao.models import OrgChangeHistory
from models.system_change_model import OrgEntity


async def add_history(data: OrgEntity, status: int):
    org_change_history = OrgChangeHistory()
    org_change_history.organization = data.org
    org_change_history.lark_user_name = data.user_name
    org_change_history.status = status
    await org_change_history.save()
