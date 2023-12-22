from dao.models import CdaUser


async def get_cda_user_by_connect_info(connect_type: str, connect_id: str) -> CdaUser:
    return await CdaUser.single('connect_type = %s and connect_id = %s', connect_type, connect_id)


async def get_cda_user_by_id(connect_type: str, user_id: str) -> CdaUser:

    return await CdaUser.single('connect_type = %s and id = %s', connect_type, user_id)
