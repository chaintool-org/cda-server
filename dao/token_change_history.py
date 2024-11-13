from dao.models import TokenChangeHistory


async def add_history(user_name: str, token: str, status: int):
    token_change_history = TokenChangeHistory()
    token_change_history.token = token
    token_change_history.lark_user_name = user_name
    token_change_history.status = status
    await token_change_history.save()
