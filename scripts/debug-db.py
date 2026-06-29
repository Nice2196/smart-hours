#!/usr/bin/env python3.11
"""
调试脚本：查询微信云开发数据库
用于定位数据问题，不需要部署云函数

用法:
  python3.11 scripts/debug-db.py                  # 全量概览（课程+排课+锁+最近消课）
  python3.11 scripts/debug-db.py --lessons 20      # 查最近20条消课记录
  python3.11 scripts/debug-db.py --course 围棋     # 查指定课程详情（消课+排课+锁）
  python3.11 scripts/debug-db.py --locks           # 查所有幂等锁
  python3.11 scripts/debug-db.py --schedules       # 查所有排课
  python3.11 scripts/debug-db.py --orphans         # 查孤儿锁（有锁无记录）
  python3.11 scripts/debug-db.py --query 'db.collection("courses").get()'  # 自定义查询
"""

import json
import ssl
import sys
import urllib.request
from datetime import datetime, timezone

# 禁用 SSL 证书验证（旧系统证书问题）
ssl._create_default_https_context = ssl._create_unverified_context

# 配置
APPID = "wx73b9c9702f51e839"
APPSECRET = "b4165d1d0d4b6a1d27bcf4bd1219a2dc"
ENV_ID = "cloud1-d7gjypgxued9a2b27"

WEEKDAY_LABELS = {
    0: "周日",
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
}


def get_access_token():
    """获取 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    resp = urllib.request.urlopen(url, timeout=10)
    data = json.loads(resp.read().decode("utf-8"))
    if "access_token" not in data:
        print(f"[ERROR] 获取 access_token 失败: {data}")
        sys.exit(1)
    return data["access_token"]


def query_db(token, collection, where="", order_by="", limit=100):
    """查询云开发数据库，返回 dict 列表"""
    url = f"https://api.weixin.qq.com/tcb/databasequery?access_token={token}"
    query = f'db.collection("{collection}")'
    if where:
        query += f".where({where})"
    if order_by:
        query += f".orderBy({order_by})"
    query += f".limit({limit}).get()"

    payload = json.dumps({"env": ENV_ID, "query": query}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode("utf-8"))

    if data.get("errcode", 0) != 0:
        print(f"[ERROR] 查询 {collection} 失败: {data}")
        return []

    records = []
    for item in data.get("data", []):
        try:
            records.append(json.loads(item) if isinstance(item, str) else item)
        except Exception:
            records.append(item)
    return records


def raw_query(token, query_str):
    """执行原始查询语句"""
    url = f"https://api.weixin.qq.com/tcb/databasequery?access_token={token}"
    payload = json.dumps({"env": ENV_ID, "query": query_str}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode("utf-8"))
    if data.get("errcode", 0) != 0:
        print(f"[ERROR] 查询失败: {data}")
        return []
    records = []
    for item in data.get("data", []):
        try:
            records.append(json.loads(item) if isinstance(item, str) else item)
        except Exception:
            records.append(item)
    return records


def format_date(date_val):
    """格式化 MongoDB 日期（支持 $date int/str 和普通字符串）"""
    if not date_val:
        return "无"
    if isinstance(date_val, dict) and "$date" in date_val:
        raw = date_val["$date"]
        if isinstance(raw, int):
            return datetime.fromtimestamp(raw / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M"
            )
        elif isinstance(raw, str):
            return raw[:16]
    if isinstance(date_val, str):
        return date_val[:16]
    return str(date_val)[:16]


def format_date_short(date_val):
    """短日期格式 MM-DD HH:MM"""
    full = format_date(date_val)
    if len(full) > 10:
        return full[5:]  # 去掉年份
    return full


def days_until(date_val):
    """计算距今天数（正数=未来，负数=已过）"""
    if not date_val:
        return None
    if isinstance(date_val, dict) and "$date" in date_val:
        raw = date_val["$date"]
        if isinstance(raw, int):
            dt = datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return (dt - datetime.now(timezone.utc)).days
    return None


# ============================================================
# 打印函数
# ============================================================


def print_courses(token):
    """打印所有课程概览"""
    courses = query_db(token, "courses")
    print(f"\n{'=' * 70}")
    print(f"  课程列表 ({len(courses)} 门)")
    print(f"{'=' * 70}")
    print(
        f"  {'名称':<8} {'状态':<10} {'总课时':>6} {'已消':>6} {'剩余':>6} {'过期日期':<20}"
    )
    print(f"  {'─' * 8} {'─' * 10} {'─' * 6} {'─' * 6} {'─' * 6} {'─' * 20}")
    for c in courses:
        name = c.get("name", "?")
        status = c.get("status", "?")
        total = c.get("totalHours", 0)
        consumed = c.get("consumedHours", 0)
        remaining = c.get("remainingHours", 0)
        expiry = format_date(c.get("expiryDate"))
        days = days_until(c.get("expiryDate"))
        if days is not None and days <= 90:
            expiry += f" ({days}天)"
        # 数据一致性检查
        flag = " ⚠️" if consumed + remaining != total else ""
        print(
            f"  {name:<8} {status:<10} {total:>6} {consumed:>6} {remaining:>6} {expiry}{flag}"
        )
    return courses


def print_lessons(token, course_name=None, limit=20):
    """打印消课记录"""
    if course_name:
        courses = query_db(token, "courses", where=f'{{name: "{course_name}"}}')
        if not courses:
            print(f"  未找到课程: {course_name}")
            return []
        cid = courses[0]["_id"]
        lessons = query_db(
            token,
            "lesson_records",
            where=f'{{courseId: "{cid}"}}',
            order_by='"lessonDate", "desc"',
            limit=limit,
        )
    else:
        lessons = query_db(
            token, "lesson_records", order_by='"lessonDate", "desc"', limit=limit
        )

    title = f"「{course_name}」" if course_name else "全部"
    print(f"\n{'=' * 70}")
    print(f"  消课记录 ({title}, 最近{limit}条)")
    print(f"{'=' * 70}")
    print(
        f"  {'日期':<12} {'时间':<8} {'课程':<8} {'类型':<8} {'扣除':>4} {'前→后':<12}"
    )
    print(f"  {'─' * 12} {'─' * 8} {'─' * 8} {'─' * 8} {'─' * 4} {'─' * 12}")
    for l in lessons:
        date = format_date(l.get("lessonDate"))
        time = l.get("scheduledTime", "-")
        name = l.get("courseName", "?")[:6]
        dtype = l.get("deductionType", "?")
        hours = l.get("deductionHours", 0)
        before = l.get("beforeConsumed", "?")
        after = l.get("afterConsumed", "?")
        print(
            f"  {date:<12} {time:<8} {name:<8} {dtype:<8} {hours:>4} {before}→{after}"
        )
    return lessons


def print_schedules(token, course_name=None):
    """打印排课"""
    if course_name:
        courses = query_db(token, "courses", where=f'{{name: "{course_name}"}}')
        if not courses:
            print(f"  未找到课程: {course_name}")
            return []
        cid = courses[0]["_id"]
        schedules = query_db(
            token, "schedules", where=f'{{courseId: "{cid}", status: "active"}}'
        )
    else:
        schedules = query_db(token, "schedules", where='{status: "active"}')

    title = f"「{course_name}」" if course_name else "全部"
    print(f"\n{'=' * 70}")
    print(f"  排课 ({title}, {len(schedules)} 条)")
    print(f"{'=' * 70}")
    print(f"  {'星期':<6} {'时间':<8} {'课程':<10} {'有效期':<30}")
    print(f"  {'─' * 6} {'─' * 8} {'─' * 10} {'─' * 30}")
    for s in schedules:
        dow = s.get("dayOfWeek", -1)
        weekday = WEEKDAY_LABELS.get(dow, f"?({dow})")
        time = s.get("time", "?")
        name = s.get("courseName", "?")[:8]
        eff_from = format_date_short(s.get("effectiveFrom")) or "无"
        eff_to = format_date_short(s.get("effectiveTo")) or "永久"
        print(f"  {weekday:<6} {time:<8} {name:<10} {eff_from} ~ {eff_to}")
    return schedules


def print_locks(token, limit=30):
    """打印幂等锁"""
    locks = query_db(token, "deduction_locks", limit=limit)
    print(f"\n{'=' * 70}")
    print(f"  幂等锁 ({len(locks)} 条)")
    print(f"{'=' * 70}")
    for l in locks:
        key = l.get("lockKey", "?")
        created = format_date_short(l.get("createdAt"))
        deleted = " [已删除]" if key.startswith("_deleted") else ""
        print(f"  {key}  ({created}){deleted}")
    return locks


def check_orphans(token):
    """检查孤儿锁（有锁无对应消课记录）"""
    locks = query_db(token, "deduction_locks", limit=100)
    lessons = query_db(token, "lesson_records", limit=200)

    # 建立 lesson 索引: courseId_scheduleId_date
    lesson_keys = set()
    for l in lessons:
        lid = l.get("lessonDate", {})
        if isinstance(lid, dict) and "$date" in lid:
            raw = lid["$date"]
            if isinstance(raw, int):
                ds = datetime.fromtimestamp(raw / 1000, tz=timezone.utc).strftime(
                    "%Y-%m-%d"
                )
            else:
                ds = str(raw)[:10]
        else:
            ds = str(lid)[:10] if lid else ""
        key = f"{l.get('courseId', '')}_{l.get('scheduleId', '')}_{ds}"
        lesson_keys.add(key)

    print(f"\n{'=' * 70}")
    print("  孤儿锁检查 (有锁无记录)")
    print(f"{'=' * 70}")
    orphans = []
    for l in locks:
        lk = l.get("lockKey", "")
        if lk.startswith("_deleted"):
            continue
        # lockKey 格式: courseId_scheduleId_YYYY-MM-DD
        parts = lk.rsplit("_", 1)
        if len(parts) == 2:
            prefix, date_str = parts
            if date_str not in lesson_keys:
                # 进一步检查是否真的没有匹配
                matching = [
                    k for k in lesson_keys if k.startswith(prefix) and date_str in k
                ]
                if not matching:
                    orphans.append(l)
                    print(f"  ⚠️ {lk}  (创建: {format_date_short(l.get('createdAt'))})")

    if not orphans:
        print("  ✓ 无孤儿锁")
    else:
        print(f"\n  共 {len(ors := orphans)} 条孤儿锁，可用 --fix-orphans 修复")
    return orphans


def check_data_consistency(token):
    """检查课程数据一致性（consumedHours vs lesson_records）"""
    courses = query_db(token, "courses")
    print(f"\n{'=' * 70}")
    print("  数据一致性检查")
    print(f"{'=' * 70}")
    issues = []
    for c in courses:
        cid = c["_id"]
        name = c.get("name", "?")
        consumed = c.get("consumedHours", 0)
        total = c.get("totalHours", 0)
        remaining = c.get("remainingHours", 0)

        # 查实际消课记录数
        lessons = query_db(
            token, "lesson_records", where=f'{{courseId: "{cid}"}}', limit=200
        )
        actual_consumed = sum(l.get("deductionHours", 0) for l in lessons)

        if consumed != actual_consumed:
            flag = "⚠️"
            issues.append(
                {"name": name, "db": consumed, "actual": actual_consumed, "cid": cid}
            )
        else:
            flag = "✓"
        if consumed + remaining != total:
            flag = "⚠️"
            if not any(i["cid"] == cid for i in issues):
                issues.append(
                    {
                        "name": name,
                        "db_consumed": consumed,
                        "db_remaining": remaining,
                        "total": total,
                        "cid": cid,
                    }
                )

        print(
            f"  {flag} {name:<8} DB已消={consumed} 实际已消={actual_consumed} 剩余={remaining} 总={total}"
        )

    if not issues:
        print("  ✓ 所有数据一致")
    return issues


def print_course_detail(token, course_name):
    """打印指定课程的完整详情"""
    courses = query_db(token, "courses", where=f'{{name: "{course_name}"}}')
    if not courses:
        print(f"  未找到课程: {course_name}")
        return
    c = courses[0]
    cid = c["_id"]
    print(f"\n{'=' * 70}")
    print(f"  课程详情: {course_name}")
    print(f"{'=' * 70}")
    print(f"  ID: {cid}")
    print(f"  状态: {c.get('status')}")
    print(
        f"  总课时: {c.get('totalHours')}  已消: {c.get('consumedHours')}  剩余: {c.get('remainingHours')}"
    )
    print(f"  过期: {format_date(c.get('expiryDate'))}")
    print()

    print_lessons(token, course_name, limit=20)
    print_schedules(token, course_name)

    # 该课程的锁
    locks = query_db(token, "deduction_locks", limit=50)
    course_locks = [l for l in locks if cid in l.get("lockKey", "")]
    print(f"\n  相关幂等锁 ({len(course_locks)} 条):")
    for l in course_locks:
        print(f"    {l.get('lockKey', '?')}  ({format_date_short(l.get('createdAt'))})")


# ============================================================
# 主入口
# ============================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="微信云开发数据库调试查询")
    parser.add_argument("--course", help="查看指定课程详情（课程名）")
    parser.add_argument(
        "--lessons", type=int, nargs="?", const=20, help="查看消课记录（默认20条）"
    )
    parser.add_argument("--schedules", action="store_true", help="查看所有排课")
    parser.add_argument("--locks", action="store_true", help="查看所有幂等锁")
    parser.add_argument("--orphans", action="store_true", help="检查孤儿锁")
    parser.add_argument("--check", action="store_true", help="数据一致性检查")
    parser.add_argument("--query", help="执行原始查询语句")
    args = parser.parse_args()

    print("=" * 70)
    print("  微信云开发数据库调试查询")
    print("=" * 70)

    token = get_access_token()
    print("  ✓ access_token 获取成功")

    # 自定义查询
    if args.query:
        results = raw_query(token, args.query)
        print(f"\n  返回 {len(results)} 条记录:")
        for r in results:
            print(f"  {json.dumps(r, ensure_ascii=False, indent=2)}")
        return

    # 指定课程详情
    if args.course:
        print_course_detail(token, args.course)
        return

    # 单独查看
    if args.lessons is not None:
        print_lessons(token, limit=args.lessons)
        return
    if args.schedules:
        print_schedules(token)
        return
    if args.locks:
        print_locks(token)
        return
    if args.orphans:
        check_orphans(token)
        return
    if args.check:
        check_data_consistency(token)
        return

    # 默认：全量概览
    print_courses(token)
    print_lessons(token, limit=10)
    print_schedules(token)
    print_locks(token)
    check_data_consistency(token)

    print(f"\n{'=' * 70}")
    print("  查询完成  (用 --help 查看更多选项)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
