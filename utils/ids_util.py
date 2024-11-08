import hashlib
import random
import string
from datetime import datetime


def generate_unique_id(user_id: str) -> str:
    # 获取当前时间
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')

    # 生成随机字符串
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    # 拼接时间、用户ID、随机字符串
    raw_string = f"{timestamp}_{user_id}_{random_str}"

    # 使用 SHA-256 哈希后取前32位
    unique_id = hashlib.sha256(raw_string.encode()).hexdigest()[:32]

    return unique_id
