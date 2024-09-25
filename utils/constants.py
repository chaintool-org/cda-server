import json
import os

CONNECT_TYPE_TELEGRAM = 'TELEGRAM'


# 发消息的testMode
test_mode = json.loads(os.getenv('SEND_MESSAGE_LIST', '["dev", "test", "prod"]'))
# 发送消息的token
send_message_token = json.loads(os.getenv('SEND_MESSAGE_TOKEN',
                                          '{"dev": {"token": "6767843762:AAGSVGuWWW7bAqRLProaQxPbN1MzLpmZS1g",'
                                          ' "chat_id": "-4539437068","tg_name":"@qimashejian2Bot"},'
                                          '"test": {"token": "6719660314:AAHnyhfgS6An6Ff2RcjT679xPWLhgSXfseo",'
                                          ' "chat_id": "-1002111465087"},'
                                          '"prod": {"token": "6566268578:AAGc4sGBLHlIpCBBtUBCJDVu4fzP5IdhUeg", '
                                          '"chat_id": "-1001280903433","tg_name":"@CDAReporterBot"} }'))


