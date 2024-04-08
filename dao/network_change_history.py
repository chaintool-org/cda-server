from dao.models import OrgChangeHistory, NetworkChangeHistory
from models.system_change_model import NetworkEntity


async def add_history(data: NetworkEntity, status: int):
    network_change_history = NetworkChangeHistory()
    network_change_history.network = data.network
    network_change_history.lark_user_name = data.user_name
    network_change_history.status = status
    await network_change_history.save()
