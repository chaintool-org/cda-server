import json

from fastapi import APIRouter, Request

from framework.result_enc import suc_enc

router = APIRouter()


@router.get("/address/config")
async def get_config():
    networks_file = "static/networks.json"
    categories_file = "static/categories.json"

    return suc_enc({
        "networks": get_json_data(networks_file),
        "categories": get_json_data(categories_file)
    })


@router.post("/address/report")
async def report_address():
    return


def get_json_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
