# SPEC: Date Utils 工具库

> 技术规格 | 2026-06-14 | feature/date-utils

## 1. Summary
Python 日期工具库，提供常用的日期计算、格式化、工作日判断功能。

## 2. Architecture
```
src/date_utils/
├── __init__.py       # 公共 API 导出
├── calc.py           # 日期计算（add_days, diff_days）
├── format.py         # 格式化（to_iso, to_chinese）
└── workday.py        # 工作日（is_workday, next_workday）
```

## 3. API Design
| 函数 | 签名 | 说明 |
|------|------|------|
| `add_days` | `(date_str, n) -> str` | 日期加n天，返回 ISO 字符串 |
| `diff_days` | `(d1, d2) -> int` | 两个日期间隔天数 |
| `to_iso` | `(date_str) -> str` | 转为 ISO 8601 格式 |
| `to_chinese` | `(date_str) -> str` | 转为中文格式 "2026年6月14日" |
| `is_workday` | `(date_str) -> bool` | 是否工作日（周一~周五） |
| `next_workday` | `(date_str) -> str` | 下一个工作日 |

## 4. Testing Strategy
- 单元测试覆盖所有 6 个函数
- 边界值：闰年、月末、跨年
- 使用 pytest.mark.parametrize 覆盖多场景
