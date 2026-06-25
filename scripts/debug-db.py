#!/usr/bin/env python3.11
"""
调试脚本：查询微信云开发数据库
用于定位数据问题，不需要部署云函数
"""

import json
import ssl
import sys
import urllib.request

# 禁用 SSL 证书验证（旧系统证书问题）
ssl._create_default_https_context = ssl._create_unverified_context

# 配置
APPID = "wx73b9c9702f51e839"
APPSECRET = "b4165d1d0d4b6a1d27bcf4bd1219a2dc"
ENV_ID = "cloud1-d7gjypgxued9a2b27"


def get_access_token():
    """获取 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    resp = urllib.request.urlopen(url, timeout=10)
    data = json.loads(resp.read().decode("utf-8"))
    if "access_token" not in data:
        print(f"[ERROR] 获取 access_token 失败: {data}")
        sys.exit(1)
    return data["access_token"]


def query_db(access_token, collection, where="", order_by="", limit=100):
    """查询云开发数据库"""
    url = f"https://api.weixin.qq.com/tcb/databasequery?access_token={access_token}"

    # 构建查询语句
    query = f"db.collection('{collection}')"
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

    # 解析返回的数据
    pager = data.get("pager", {})
    records = []
    for item_str in data.get("data", []):
        try:
            records.append(json.loads(item_str))
        except:
            records.append(item_str)

    return records


def format_date(date_val):
    """格式化日期"""
    from datetime import datetime, timezone

    if not date_val:
        return "无"
    if isinstance(date_val, dict) and "$date" in date_val:
        raw = date_val["$date"]
        if isinstance(raw, int):
            # Unix 毫秒时间戳
            dt = datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M")
        elif isinstance(raw, str):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
    return str(date_val)


def main():
    print("=" * 60)
    print("微信云开发数据库调试查询")
    print("=" * 60)

    # 获取 access_token
    print("\n[1] 获取 access_token...")
    token = get_access_token()
    print("    ✓ token 获取成功")

    # 查询所有课程
    print("\n[2] 查询 courses 集合...")
    courses = query_db(token, "courses")
    print(f"    共 {len(courses)} 门课程:\n")
    print(
        f"    {'名称':<8} {'状态':<10} {'总课时':<8} {'已消':<8} {'剩余':<8} {'过期日期':<12}"
    )
    print(f"    {'-' * 8} {'-' * 10} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 12}")

    for c in courses:
        cid = c.get("_id", "?")
        name = c.get("name", "?")
        status = c.get("status", "?")
        total = c.get("totalHours", 0)
        consumed = c.get("consumedHours", 0)
        remaining = c.get("remainingHours", 0)
        expiry = format_date(c.get("expiryDate", ""))
        print(f"    [{cid}]")

        # 检查过期日期是否在90天内
        if c.get("expiryDate"):
            from datetime import datetime, timezone

            if isinstance(c["expiryDate"], dict) and "$date" in c["expiryDate"]:
                raw = c["expiryDate"]["$date"]
                if isinstance(raw, int):
                    exp_dt = datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
                else:
                    exp_dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                days_left = (exp_dt - datetime.now(exp_dt.tzinfo)).days
                if days_left <= 90:
                    expiry += f" ({days_left}天)"

        print(
            f"    {name:<8} {status:<10} {total:<8} {consumed:<8} {remaining:<8} {expiry}"
        )

    # 查询围棋课程的消课记录
    print("\n[3] 查询围棋课程的消课记录...")
    weiqi_course = next((c for c in courses if c.get("name") == "围棋"), None)

    if weiqi_course:
        course_id = weiqi_course.get("_id", "")
        print(f"    围棋课程 ID: {course_id}")

        # 查询该课程的所有消课记录
        lessons = query_db(
            token,
            "lesson_records",
            where=f'{{courseId: "{course_id}"}}',
            order_by='"lessonDate", "desc"',
            limit=20,
        )

        print(f"    共 {len(lessons)} 条消课记录:\n")
        print(
            f"    {'日期':<12} {'时间':<8} {'类型':<8} {'扣除':<8} {'前已消':<8} {'后已消':<8}"
        )
        print(f"    {'-' * 12} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8}")

        for l in lessons:
            date = format_date(l.get("lessonDate", ""))
            time = l.get("scheduledTime", "?")
            dtype = l.get("deductionType", "?")
            hours = l.get("deductionHours", 0)
            before = l.get("beforeConsumed", "?")
            after = l.get("afterConsumed", "?")
            print(
                f"    {date:<12} {time:<8} {dtype:<8} {hours:<8} {before:<8} {after:<8}"
            )
    else:
        print("    未找到围棋课程")

    # 查询围棋的排课
    print("\n[4] 查询围棋课程的排课...")
    if weiqi_course:
        course_id = weiqi_course.get("_id", "")
        schedules = query_db(
            token,
            "schedules",
            where=f'{{courseId: "{course_id}", status: "active"}}',
        )

        WEEKDAY_LABELS = {
            0: "周日",
            1: "周一",
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六",
        }
        print(f"    共 {len(schedules)} 条排课:\n")
        for s in schedules:
            dow = s.get("dayOfWeek", "?")
            weekday = WEEKDAY_LABELS.get(dow, f"未知({dow})")
            time = s.get("time", "?")
            print(f"    {weekday} {time}")

    # 查询 deduction_locks
    print("\n[5] 查询 deduction_locks 集合...")
    locks = query_db(token, "deduction_locks", limit=20)
    print(f"    共 {len(locks)} 条锁记录:\n")
    for l in locks:
        key = l.get("lockKey", "?")
        created = format_date(l.get("createdAt", ""))
        print(f"    {key}  (创建: {created})")

    print("\n" + "=" * 60)
    print("查询完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
