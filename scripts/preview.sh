#!/bin/bash
# ============================================================
# 小程序预览脚本
# 功能：上传代码 → 生成预览二维码 → 打开预览
# 用法：./scripts/preview.sh [版本描述]
# ============================================================

set -e

# 配置
APPID="wx73b9c9702f51e839"
APPSECRET="b4165d1d0d4b6a1d27bcf4bd1219a2dc"
PROJECT_DIR="/Volumes/macSdcard/AICoding/smart-hours"
DEVTOOLS_PORT=60578

# 版本号自动递增
VERSION_FILE="$PROJECT_DIR/.version"
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
else
    CURRENT_VERSION="1.0.0"
fi

# 版本号自增（patch）
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"
echo "$NEW_VERSION" > "$VERSION_FILE"

# 版本描述
DESC="${1:-Auto preview: $NEW_VERSION}"

echo "=========================================="
echo "  小程序预览脚本"
echo "=========================================="
echo "  APPID: $APPID"
echo "  版本号: $NEW_VERSION"
echo "  描述: $DESC"
echo "=========================================="

# Step 1: 检查微信开发者工具是否运行
echo ""
echo "Step 1: 检查微信开发者工具..."
if ! curl -s "http://127.0.0.1:$DEVTOOLS_PORT" > /dev/null 2>&1; then
    echo "❌ 微信开发者工具未运行或端口未开启"
    echo "请先启动微信开发者工具并开启服务端口"
    exit 1
fi
echo "✅ 微信开发者工具已运行"

# Step 2: 上传代码
echo ""
echo "Step 2: 上传代码..."
UPLOAD_RESULT=$(curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/upload?project=$PROJECT_DIR&version=$NEW_VERSION&desc=$DESC" 2>/dev/null)

# 检查上传结果
if echo "$UPLOAD_RESULT" | grep -q '"success":true'; then
    SIZE=$(echo "$UPLOAD_RESULT" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "✅ 上传成功！包大小: $(echo "scale=2; $SIZE/1024" | bc) KB"
elif echo "$UPLOAD_RESULT" | grep -q "Redirecting"; then
    TASK_ID=$(echo "$UPLOAD_RESULT" | grep -o 'taskresult/[0-9]*' | cut -d'/' -f2)
    TASK_TIME=$(echo "$UPLOAD_RESULT" | grep -o 't=[0-9]*' | cut -d'=' -f2)
    sleep 2
    UPLOAD_RESPONSE=$(curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/taskresult/$TASK_ID?t=$TASK_TIME" 2>/dev/null)

    if echo "$UPLOAD_RESPONSE" | grep -q '"success":true'; then
        SIZE=$(echo "$UPLOAD_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
        echo "✅ 上传成功！包大小: $(echo "scale=2; $SIZE/1024" | bc) KB"
    else
        echo "❌ 上传失败: $UPLOAD_RESPONSE"
        exit 1
    fi
else
    echo "❌ 上传请求失败: $UPLOAD_RESULT"
    exit 1
fi

# Step 3: 生成预览二维码
echo ""
echo "Step 3: 生成预览二维码..."
PREVIEW_RESULT=$(curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/preview?project=$PROJECT_DIR&format=image&qroutput=terminal" 2>/dev/null)

if echo "$PREVIEW_RESULT" | grep -q "Redirecting"; then
    PREVIEW_TASK_ID=$(echo "$PREVIEW_RESULT" | grep -o 'taskresult/[0-9]*' | cut -d'/' -f2)
    PREVIEW_TASK_TIME=$(echo "$PREVIEW_RESULT" | grep -o 't=[0-9]*' | cut -d'=' -f2)

    # 等待二维码生成
    sleep 2

    # 保存二维码图片
    curl -s "http://127.0.0.1:$DEVTOOLS_PORT/v2/taskresult/$PREVIEW_TASK_ID?t=$PREVIEW_TASK_TIME" -o "$PROJECT_DIR/preview-qr.png" 2>/dev/null

    if [ -f "$PROJECT_DIR/preview-qr.png" ] && [ -s "$PROJECT_DIR/preview-qr.png" ]; then
        echo "✅ 预览二维码已保存: $PROJECT_DIR/preview-qr.png"
    else
        echo "⚠️  二维码保存失败，但代码已上传"
    fi
else
    echo "⚠️  二维码生成失败，但代码已上传"
fi

# Step 4: 完成
echo ""
echo "=========================================="
echo "  ✅ 全部完成！"
echo "=========================================="
echo ""
echo "  下一步操作："
echo "  1. 使用预览二维码扫码验证"
echo "  2. 或在微信小程序后台设置体验版"
echo ""
echo "  预览二维码: $PROJECT_DIR/preview-qr.png"
echo "=========================================="
