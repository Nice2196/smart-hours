"""工作日模块：is_workday, next_workday."""

from datetime import datetime, timedelta


def is_workday(date_str: str) -> bool:
    """判断是否为工作日（周一至周五）。

    Args:
        date_str: 日期字符串，支持 YYYY-MM-DD 或 YYYY/MM/DD

    Returns:
        True 如果是工作日，False 如果是周末

    Examples:
        >>> is_workday('2026-06-15')  # 周一
        True
        >>> is_workday('2026-06-14')  # 周日
        False
    """
    date_str = date_str.replace("/", "-")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() < 5  # 0=周一, 6=周日


def next_workday(date_str: str) -> str:
    """获取下一个工作日。

    如果当天是工作日，返回当天；否则返回下周一。

    Args:
        date_str: 日期字符串

    Returns:
        下一个工作日的 ISO 日期

    Examples:
        >>> next_workday('2026-06-14')  # 周日 → 周一
        '2026-06-15'
        >>> next_workday('2026-06-15')  # 周一 → 周一
        '2026-06-15'
    """
    date_str = date_str.replace("/", "-")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    while dt.weekday() > 4:  # 跳过周末
        dt += timedelta(days=1)
    return dt.strftime("%Y-%m-%d")
