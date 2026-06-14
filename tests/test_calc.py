"""测试日期计算模块."""

import pytest
from src.date_utils.calc import add_days, diff_days


class TestAddDays:
    """add_days 函数测试."""

    def test_add_positive_days(self):
        """正向增加天数."""
        assert add_days("2026-01-01", 5) == "2026-01-06"

    def test_add_zero_days(self):
        """增加 0 天返回原日期."""
        assert add_days("2026-06-14", 0) == "2026-06-14"

    def test_subtract_days(self):
        """负数减少天数."""
        assert add_days("2026-01-10", -3) == "2026-01-07"

    def test_slash_format(self):
        """支持 / 分隔的日期."""
        assert add_days("2026/01/01", 10) == "2026-01-11"

    def test_cross_month(self):
        """跨月计算."""
        assert add_days("2026-01-31", 1) == "2026-02-01"

    def test_cross_year(self):
        """跨年计算."""
        assert add_days("2026-12-31", 1) == "2027-01-01"


class TestDiffDays:
    """diff_days 函数测试."""

    @pytest.mark.parametrize(
        "d1,d2,expected",
        [
            ("2026-01-01", "2026-01-10", 9),
            ("2026-01-01", "2026-01-01", 0),
            ("2026-12-31", "2027-01-01", 1),
            ("2024-02-28", "2024-03-01", 2),  # 闰年
        ],
    )
    def test_diff_days(self, d1, d2, expected):
        """参数化测试日期差."""
        assert diff_days(d1, d2) == expected

    def test_slash_format(self):
        """支持 / 分隔的日期."""
        assert diff_days("2026/01/01", "2026/01/10") == 9

    def test_negative_diff(self):
        """d1 晚于 d2 返回负数."""
        assert diff_days("2026-01-10", "2026-01-01") == -9
