import re
from .number import DIGITS
from .number import num2str
from .number import verbalize_digit
from .number import verbalize_cardinal

# 时刻表达式
RE_TIME = re.compile(
    r'([0-1]?[0-9]|2[0-3])'
    r':([0-9][0-9]?)'
    r'(:([0-9][0-9]?))?')

# 时间范围，如8:30-12:30
RE_TIME_RANGE = re.compile(
    r'([0-1]?[0-9]|2[0-3])'
    r':([0-9][0-9]?)'
    r'(:([0-9][0-9]?))?'
    r'(~|-)'
    r'([0-1]?[0-9]|2[0-3])'
    r':([0-9][0-9]?)'
    r'(:([0-9][0-9]?))?')

# 年月日
RE_DATE = re.compile(
    r'(\d{4}|\d{2})年'
    r'((0?[1-9]|1[0-2])月)?'
    r'(((0?[1-9])|((1|2)[0-9])|30|31)([日号]))?')

# xxxx/xx/xx
RE_DATE2 = re.compile(
    r'(\d{4})([- /.])(0?[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])')


def _time_num2str(num_string: str) -> str:
    """A special case for verbalizing number in time."""
    result = num2str(num_string.lstrip('0'))
    if num_string.startswith('0'):
        result = DIGITS['0'] + result
    return result

def replace_time(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    is_range = len(match.groups()) > 5
    hour = match.group(1)
    minute = match.group(2)
    second = match.group(4)

    if is_range:
        hour_2 = match.group(6)
        minute_2 = match.group(7)
        second_2 = match.group(9)

    result = f"{num2str(hour)}点"
    if minute.lstrip('0'):
        if int(minute) == 30:
            result += "半"
        else:
            result += f"{_time_num2str(minute)}分"
    if second and second.lstrip('0'):
        result += f"{_time_num2str(second)}秒"

    if is_range:
        result += "至"
        result += f"{num2str(hour_2)}点"
        if minute_2.lstrip('0'):
            if int(minute) == 30:
                result += "半"
            else:
                result += f"{_time_num2str(minute_2)}分"
        if second_2 and second_2.lstrip('0'):
            result += f"{_time_num2str(second_2)}秒"

    return result

def replace_date(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    year = match.group(1)
    month = match.group(3)
    day = match.group(5)
    result = ""
    if year:
        result += f"{verbalize_digit(year)}年"
    if month:
        result += f"{verbalize_cardinal(month)}月"
    if day:
        result += f"{verbalize_cardinal(day)}{match.group(9)}"
    return result

def replace_date2(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    year = match.group(1)
    month = match.group(3)
    day = match.group(4)
    result = ""
    if year:
        result += f"{verbalize_digit(year)}年"
    if month:
        result += f"{verbalize_cardinal(month)}月"
    if day:
        result += f"{verbalize_cardinal(day)}日"
    return result
