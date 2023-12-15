from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/address/config")
async def get_config():
    return


@router.post("/address/report")
async def report_address():
    return
