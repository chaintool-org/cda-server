import re
from datetime import datetime, timedelta

format1 = '%Y/%m/%d %H:%M:%S'
format2 = '%d-%m-%Y'


# 时间解析函数
def get_time(arg1: str, arg2: str):
    dis_reg = r'^(\d{1,2})([dwm])$'
    now = datetime.utcnow()

    # 处理相对时间
    dis_match = re.match(dis_reg, arg1)
    if dis_match:
        dis, type_char = int(dis_match.group(1)), dis_match.group(2).lower()

        if type_char == 'd':  # days
            start_day = now - timedelta(days=dis - 1)
        elif type_char == 'w':  # weeks
            start_day = now - timedelta(weeks=dis)
        elif type_char == 'm':  # months (approximation using 30 days)
            start_day = now - timedelta(days=30 * dis)
        end_day = now

    # 处理日期范围
    else:
        try:
            start_day = datetime.strptime(arg1, '%d-%m-%Y')
            end_day = datetime.strptime(arg2, '%d-%m-%Y') if arg2 else start_day
        except ValueError:
            return None

        # 纠正日期顺序
        if start_day > end_day:
            start_day, end_day = end_day, start_day

    start_time = start_day.strftime('%Y/%m/%d 00:00:00')
    end_time = end_day.strftime('%Y/%m/%d 23:59:59')
    id_str = f"{start_day.strftime('%d-%m-%Y')}_{end_day.strftime('%d-%m-%Y')}" if start_day != end_day else start_day.strftime(
        '%d-%m-%Y')

    return [start_time, end_time, id_str]


async def str_time_format(date_str, from_format, to_format):
    date_obj = datetime.strptime(date_str, from_format)
    formatted_date = date_obj.strftime(to_format)
    return formatted_date

async def validate_datetime_format(date_string):
    try:
        # 尝试用指定格式解析日期字符串
        datetime.strptime(date_string, "%Y/%m/%d 00:00:00")
        return True
    except ValueError:
        # 如果解析失败则说明格式不匹配
        return False

async def validate_time_range(start_date_str, end_date_str):
    try:
        # 解析开始时间和结束时间字符串
        start_date = datetime.strptime(start_date_str, "%Y/%m/%d 00:00:00")
        end_date = datetime.strptime(end_date_str, "%Y/%m/%d 00:00:00")

        # 确保开始时间小于结束时间
        if start_date < end_date:
            return True
        else:
            return False
    except ValueError:
        # 如果解析失败则说明格式不匹配
        return False
