"""tests for greet module — get_greeting()"""

from greet import get_greeting


class TestGetGreeting:
    """get_greeting() 根据时段返回中文问候语。"""

    def test_morning(self):
        assert get_greeting(8) == "早上好"

    def test_afternoon(self):
        assert get_greeting(14) == "下午好"

    def test_evening(self):
        assert get_greeting(21) == "晚上好"

    def test_boundary_morning_start(self):
        assert get_greeting(6) == "早上好"

    def test_boundary_afternoon_start(self):
        assert get_greeting(12) == "下午好"

    def test_boundary_evening_start(self):
        assert get_greeting(18) == "晚上好"

    def test_midnight(self):
        assert get_greeting(0) == "晚上好"

    def test_early_morning(self):
        assert get_greeting(5) == "晚上好"

    def test_uses_current_time_by_default(self):
        """不传 hour 时应返回非空字符串"""
        result = get_greeting()
        assert result in ("早上好", "下午好", "晚上好")
