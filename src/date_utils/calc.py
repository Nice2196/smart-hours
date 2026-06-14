"""日期计算模块：add_days, diff_days."""

from datetime import datetime, timedelta


def add_days(date_str: str, n: int) -> str:
    """日期加 n 天，返回 ISO 格式字符串。

    Args:
        date_str: 日期字符串，支持 YYYY-MM-DD 或 YYYY/MM/DD
        n: 增加天数（可为负数）

    Returns:
        ISO 8601 日期字符串 YYYY-MM-DD

    Examples:
        >>> add_days('2026-01-01', 5)
        '2026-01-06'
    """
    date_str = date_str.replace("/", "-")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    result = dt + timedelta(days=n)
    return result.strftime("%Y-%m-%d")


def diff_days(d1: str, d2: str) -> int:
    """计算两个日期的间隔天数。

    Args:
        d1: 较早日期
        d2: 较晚日期

    Returns:
        间隔天数（d2 - d1）

    Examples:
        >>> diff_days('2026-01-01', '2026-01-10')
        9
    """
    d1 = d1.replace("/", "-")
    d2 = d2.replace("/", "-")
    dt1 = datetime.strptime(d1, "%Y-%m-%d")
    dt2 = datetime.strptime(d2, "%Y-%m-%d")
    return (dt2 - dt1).days
