"""测试日期格式化模块."""

import pytest
from src.date_utils.format import to_chinese, to_iso


class TestToIso:
    """to_iso 函数测试."""

    def test_iso_input(self):
        """ISO 格式输入不变."""
        assert to_iso("2026-06-14") == "2026-06-14"

    def test_slash_input(self):
        """斜杠输入转 ISO."""
        assert to_iso("2026/06/14") == "2026-06-14"

    def test_chinese_input(self):
        """中文日期输入转 ISO."""
        assert to_iso("2026年6月14日") == "2026-06-14"

    def test_chinese_single_digit_month(self):
        """中文日期单数月."""
        assert to_iso("2026年3月5日") == "2026-03-05"

    @pytest.mark.parametrize(
        "input_date,expected",
        [
            ("2026-01-01", "2026-01-01"),
            ("2026/12/31", "2026-12-31"),
            ("2026年1月1日", "2026-01-01"),
            ("2026年10月31日", "2026-10-31"),
        ],
    )
    def test_to_iso_variants(self, input_date, expected):
        """参数化测试多种输入格式."""
        assert to_iso(input_date) == expected


class TestToChinese:
    """to_chinese 函数测试."""

    def test_iso_input(self):
        """ISO 输入转中文."""
        assert to_chinese("2026-06-14") == "2026年6月14日"

    def test_slash_input(self):
        """斜杠输入转中文."""
        assert to_chinese("2026/06/14") == "2026年6月14日"

    def test_single_digit(self):
        """单数字日期."""
        assert to_chinese("2026-03-05") == "2026年3月5日"
