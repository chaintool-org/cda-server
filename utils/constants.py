import json
import os

CONNECT_TYPE_TELEGRAM = 'TELEGRAM'


# 发消息的testMode
test_mode = json.loads(os.getenv('SEND_MESSAGE_LIST', '["dev", "test", "prod"]'))
# 发送消息的token
send_message_token = json.loads(os.getenv('SEND_MESSAGE_TOKEN',
                                          '{"dev": {"token": "7853704896:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E",'
                                          ' "chat_ids": ["-4539437068","-1002536630151_22"]},'
                                          '"test": {"token": "7853704896:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E",'
                                          ' "chat_ids": ["-1002111465087","-1002536630151_22"]},'
                                          '"prod": {"token": "6566268578:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E", '
                                          '"chat_ids": ["-1001280903433", "-1002622004671_3"],"tg_name":"@CDAReporterBot"} }'))
