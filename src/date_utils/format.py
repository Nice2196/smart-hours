"""日期格式化模块：to_iso, to_chinese."""

from datetime import datetime


def to_iso(date_str: str) -> str:
    """将日期字符串转为 ISO 8601 格式。

    Args:
        date_str: 支持 YYYY-MM-DD、YYYY/MM/DD、YYYY年M月D日

    Returns:
        YYYY-MM-DD 格式字符串

    Examples:
        >>> to_iso('2026/06/14')
        '2026-06-14'
        >>> to_iso('2026年6月14日')
        '2026-06-14'
    """
    date_str = (
        date_str.replace("/", "-")
        .replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
    )
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y-%m-%d")


def to_chinese(date_str: str) -> str:
    """将日期字符串转为中文格式。

    Args:
        date_str: 支持 YYYY-MM-DD、YYYY/MM/DD

    Returns:
        XXXX年X月X日 格式

    Examples:
        >>> to_chinese('2026-06-14')
        '2026年6月14日'
    """
    date_str = date_str.replace("/", "-")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.year}年{dt.month}月{dt.day}日"
