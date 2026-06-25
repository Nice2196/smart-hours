#!/usr/bin/env python3.11
"""
修复数据库中的数据问题：
1. 修复写字(88课时)的 expiryDate 格式（字符串 → Date 对象）
2. 修复围棋的 consumedHours（从2改为1，因为6/24的第二条消课失败了）
"""

import json
import ssl
import sys
import urllib.request

# 禁用 SSL 证书验证
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


def update_db(access_token, collection, doc_id, update_data):
    """更新云开发数据库文档"""
    url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={access_token}"

    # 构建更新语句
    set_clause = json.dumps(update_data)
    query = (
        f"db.collection('{collection}').doc('{doc_id}').update({{data: {set_clause}}})"
    )

    payload = json.dumps({"env": ENV_ID, "query": query}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode("utf-8"))

    if data.get("errcode", 0) != 0:
        print(f"[ERROR] 更新 {collection} 失败: {data}")
        return False

    print(f"    ✓ 更新成功: {data}")
    return True


def main():
    print("=" * 60)
    print("数据库修复脚本")
    print("=" * 60)

    # 获取 access_token
    print("\n[1] 获取 access_token...")
    token = get_access_token()
    print("    ✓ token 获取成功")

    # 修复1: 写字(88课时)的 expiryDate
    print("\n[2] 修复写字(88课时)的 expiryDate 格式...")
    print("    课程 ID: 54ef21436a3d1ae500093e27079d2894")
    print("    修复: '2026-07-19' → Date(2026-07-19)")

    # 使用 db.serverDate() 或直接使用 ISO 字符串
    # 微信云开发 HTTP API 使用自己的语法
    url = f"https://api.weixin.qq.com/tcb/databaseupdate?access_token={token}"
    query = "db.collection('courses').doc('54ef21436a3d1ae500093e27079d2894').update({data: {expiryDate: db.serverDate()}})"

    # 尝试直接使用 ISO 字符串格式
    query = "db.collection('courses').doc('54ef21436a3d1ae500093e27079d2894').update({data: {expiryDate: new Date('2026-07-19T00:00:00.000Z')}})"

    payload = json.dumps({"env": ENV_ID, "query": query}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode("utf-8"))

    if data.get("errcode", 0) != 0:
        print(f"    [ERROR] 更新失败: {data}")
    else:
        print(f"    ✓ 更新成功: {data}")

    # 修复2: 围棋的 consumedHours
    print("\n[3] 修复围棋的 consumedHours...")
    print("    课程 ID: a1edb8906a3a98a200078e75736f33b1")
    print("    修复: consumedHours 2 → 1, remainingHours 48 → 49")

    update_data = {"consumedHours": 1, "remainingHours": 49}
    update_db(token, "courses", "a1edb8906a3a98a200078e75736f33b1", update_data)

    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)
    print("\n注意: 修复后需要刷新小程序页面才能看到效果")


if __name__ == "__main__":
    main()
