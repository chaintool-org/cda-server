from fastapi import APIRouter, Request

from framework.exceptions import BusinessException

router = APIRouter()


@router.get("/test")
async def test():
    raise BusinessException(1001, 'test except')
