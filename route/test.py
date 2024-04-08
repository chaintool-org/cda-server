import csv

from fastapi import APIRouter, Request

from dao import cda_organization_dao, cda_address_report_dao
from dao.models import CdaOrganization, CdaNetwork
from framework.exceptions import BusinessException
from models.report_address_model import DataEntry
from route.address_route import make_cda_address_report_data
from utils.file_util import get_json_data

router = APIRouter()


@router.get("/test")
async def test():
    # networks_file = "static/json/networks.json"
    # categories_file = "static/json/categories.json"
    # telegram_message_file = "static/html/telegram_message.html"
    #
    # networks = get_json_data(networks_file)
    # for item in networks:
    #     data = CdaNetwork()
    #     data.network= item
    #     await data.save()
    # csv_file_path = 'static/json/GINT1186.csv'
    #
    # # 创建一个空的列表，用于存储数据
    # data_array = []
    #
    # # 打开 CSV 文件
    # with open(csv_file_path, 'r') as file:
    #     # 创建 CSV 读取器
    #     csv_reader = csv.reader(file)
    #
    #     # 如果 CSV 文件包含标题行，可以跳过
    #     # next(csv_reader)
    #
    #     # 读取文件中的数据并将每行添加到数组
    #     for row in csv_reader:
    #
    #         data_array.append(row)
    #     data_model = DataEntry()
    #     data_model.addresses = data_array
    #     data_model.network = 'BTC'
    #     data_model.category = 'Unspent funds from Ransomware'
    #     data_model.public = 0
    #     data_model.source = 'LE report to Exchanges Reporter'
    # # 打印整个数组
    # print(data_array)
    # # await cda_address_report_dao.inserts_cda_address_report(
    # #     make_cda_address_report_data(json_data.data, last_inserted_id, cda_user.organization, json_data.testMode))
    return "ok"
