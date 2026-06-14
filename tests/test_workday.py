"""测试工作日模块."""

import pytest
from src.date_utils.workday import is_workday, next_workday


class TestIsWorkday:
    """is_workday 函数测试."""

    def test_monday_is_workday(self):
        """周一是工作日."""
        assert is_workday("2026-06-15") is True  # 周一

    def test_sunday_is_not_workday(self):
        """周日不是工作日."""
        assert is_workday("2026-06-14") is False  # 周日

    def test_saturday_is_not_workday(self):
        """周六不是工作日."""
        assert is_workday("2026-06-20") is False  # 周六

    def test_friday_is_workday(self):
        """周五是工作日."""
        assert is_workday("2026-06-19") is True  # 周五

    def test_slash_format(self):
        """支持 / 分隔的日期."""
        assert is_workday("2026/06/15") is True


class TestNextWorkday:
    """next_workday 函数测试."""

    def test_sunday_to_monday(self):
        """周日返回下周一."""
        assert next_workday("2026-06-14") == "2026-06-15"  # 周日→周一

    def test_saturday_to_monday(self):
        """周六返回下周一."""
        assert next_workday("2026-06-20") == "2026-06-22"  # 周六→周一

    def test_monday_stays_monday(self):
        """周一返回当天."""
        assert next_workday("2026-06-15") == "2026-06-15"  # 周一

    def test_friday_stays_friday(self):
        """周五返回当天."""
        assert next_workday("2026-06-19") == "2026-06-19"  # 周五

    @pytest.mark.parametrize(
        "input_date,expected",
        [
            ("2026-06-13", "2026-06-15"),  # 周六→周一
            ("2026-06-14", "2026-06-15"),  # 周日→周一
            ("2026-06-15", "2026-06-15"),  # 周一→周一
            ("2026-06-19", "2026-06-19"),  # 周五→周五
        ],
    )
    def test_next_workday_variants(self, input_date, expected):
        """参数化测试工作日推算."""
        assert next_workday(input_date) == expected
