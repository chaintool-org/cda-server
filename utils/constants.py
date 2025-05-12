import json
import os

CONNECT_TYPE_TELEGRAM = 'TELEGRAM'


# 发消息的testMode
test_mode = json.loads(os.getenv('SEND_MESSAGE_LIST', '["dev", "test", "prod"]'))
# 发送消息的token
send_message_token = json.loads(os.getenv('SEND_MESSAGE_TOKEN',
                                          '{"dev": {"token": "7853704896:AAHnyhfgS6An6Ff2RcjT679xPWLhgSXfseo",'
                                          ' "chat_ids": ["-4539437068","-1002536630151"]},'
                                          '"test": {"token": "6719660314:AAHnyhfgS6An6Ff2RcjT679xPWLhgSXfseo",'
                                          ' "chat_ids": ["-1002111465087","-1002536630151"]},'
                                          '"prod": {"token": "6566268578:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E", '
                                          '"chat_ids": ["-1001280903433", "-1002622004671"],"tg_name":"@CDAReporterBot"} }'))
