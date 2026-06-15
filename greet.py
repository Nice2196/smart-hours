"""时间问候语模块 —— 根据当前小时自动返回中文问候语。

边界定义:
  [6, 12)   → 早上好
  [12, 18)  → 下午好
  [18, 24) ∪ [0, 6) → 晚上好
"""

from datetime import datetime


def get_greeting(hour: int | None = None) -> str:
    """返回当前时段的中文问候语。

    Args:
        hour: 可选，手动指定小时 (0-23)。不传则使用当前时间。
    """
    if hour is None:
        hour = datetime.now().hour

    if 6 <= hour < 12:
        return "早上好"
    elif 12 <= hour < 18:
        return "下午好"
    else:
        return "晚上好"


if __name__ == "__main__":
    print(get_greeting())
