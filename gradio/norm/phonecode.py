import re
from .number import verbalize_digit

# 规范化固话
RE_TELEPHONE = re.compile(
    r"(?<!\d)((0(10|2[1-3]|[3-9]\d{2})-?)?[1-9]\d{7,8})(?!\d)")

# 规范化手机号
RE_MOBILE_PHONE = re.compile(
    r"(?<!\d)((\+?86 ?)?1([38]\d|5[0-35-9]|7[678]|9[89])\d{8})(?!\d)")

# 全国统一的号码400开头
RE_NATIONAL_UNIFORM_NUMBER = re.compile(r"(400)(-)?\d{3}(-)?\d{4}")


def phone2str(phone_string: str, mobile=True) -> str:
    if mobile:
        sp_parts = phone_string.strip('+').split()
        result = '，'.join(
            [verbalize_digit(part, alt_one=True) for part in sp_parts])
        return result
    else:
        sil_parts = phone_string.split('-')
        result = '，'.join(
            [verbalize_digit(part, alt_one=True) for part in sil_parts])
        return result


def replace_phone(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    return phone2str(match.group(0), mobile=False)


def replace_mobile(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    return phone2str(match.group(0))
