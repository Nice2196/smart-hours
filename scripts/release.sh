#!/bin/bash
# ============================================================
# 小程序发布脚本
# 功能：上传代码 → 获取 access_token → 设置体验版 → 获取体验码
# 用法：./scripts/release.sh [版本描述]
# ============================================================

set -e

# 配置
APPID="wx73b9c9702f51e839"
APPSECRET="b4165d1d0d4b6a1d27bcf4bd1219a2dc"
PROJECT_DIR="/Volumes/macSdcard/AICoding/smart-hours"
DEVTOOLS_PORT=60578
OUTPUT_DIR="$PROJECT_DIR/release"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 版本号自动递增
VERSION_FILE="$PROJECT_DIR/.version"
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
else
    CURRENT_VERSION="1.0.0"
fi

IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"
echo "$NEW_VERSION" > "$VERSION_FILE"

DESC="${1:-Release $NEW_VERSION}"

echo "=========================================="
echo "  小程序发布脚本"
echo "=========================================="
echo "  APPID: $APPID"
echo "  版本号: $NEW_VERSION"
echo "  描述: $DESC"
echo "=========================================="

# Step 1: 检查微信开发者工具
echo ""
echo "Step 1: 检查微信开发者工具..."
if ! curl -s "http://127.0.0.1:$DEVTOOLS_PORT" > /dev/null 2>&1; then
    echo "❌ 微信开发者工具未运行"
    exit 1
fi
echo "✅ 微信开发者工具已运行"

# Step 2: 上传代码
echo ""
echo "Step 2: 上传代码..."
UPLOAD_RESULT=$(curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/upload?project=$PROJECT_DIR&version=$NEW_VERSION&desc=$DESC" 2>/dev/null)

if echo "$UPLOAD_RESULT" | grep -q '"success":true'; then
    echo "✅ 上传成功！"
elif echo "$UPLOAD_RESULT" | grep -q "Redirecting"; then
    TASK_ID=$(echo "$UPLOAD_RESULT" | grep -o 'taskresult/[0-9]*' | cut -d'/' -f2)
    TASK_TIME=$(echo "$UPLOAD_RESULT" | grep -o 't=[0-9]*' | cut -d'=' -f2)
    sleep 2
    UPLOAD_RESPONSE=$(curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/taskresult/$TASK_ID?t=$TASK_TIME" 2>/dev/null)

    if echo "$UPLOAD_RESPONSE" | grep -q '"success":true'; then
        echo "✅ 上传成功！"
    else
        echo "❌ 上传失败"
        exit 1
    fi
else
    echo "❌ 上传请求失败"
    exit 1
fi

# Step 3: 获取 access_token
echo ""
echo "Step 3: 获取 access_token..."
TOKEN_RESPONSE=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=$APPID&secret=$APPSECRET" 2>/dev/null)

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
EXPIRES_IN=$(echo "$TOKEN_RESPONSE" | grep -o '"expires_in":[0-9]*' | cut -d':' -f2)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ 获取 access_token 失败: $TOKEN_RESPONSE"
    echo "请检查 APPID 和 APPSECRET 是否正确"
    exit 1
fi
echo "✅ access_token 获取成功（有效期: ${EXPIRES_IN}s）"

# Step 4: 获取体验版二维码
echo ""
echo "Step 4: 获取体验版二维码..."
QR_RESPONSE=$(curl -s -X POST "https://api.weixin.qq.com/wxa/get_qrcode?access_token=$ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -o "$OUTPUT_DIR/experience-qr.png" 2>/dev/null)

if [ -f "$OUTPUT_DIR/experience-qr.png" ] && [ -s "$OUTPUT_DIR/experience-qr.png" ]; then
    # 检查是否是 JSON 错误响应
    if file "$OUTPUT_DIR/experience-qr.png" | grep -q "JSON\|text"; then
        echo "❌ 获取体验码失败"
        cat "$OUTPUT_DIR/experience-qr.png"
        exit 1
    fi
    echo "✅ 体验版二维码已保存: $OUTPUT_DIR/experience-qr.png"
else
    echo "❌ 体验版二维码获取失败"
    exit 1
fi

# Step 5: 完成
echo ""
echo "=========================================="
echo "  ✅ 发布完成！"
echo "=========================================="
echo ""
echo "  版本号: $NEW_VERSION"
echo "  体验码: $OUTPUT_DIR/experience-qr.png"
echo ""
echo "  下一步："
echo "  1. 扫描体验码验证功能"
echo "  2. 确认无误后在后台提交审核"
echo "=========================================="
