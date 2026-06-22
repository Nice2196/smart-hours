# 部署指南

本文档指导你将 **智慧课时管理（SmartHours）** 微信小程序部署上线。

---

## 1. 前置条件

| 项目 | 要求 |
|------|------|
| 微信开发者工具 | 最新稳定版，已登录并关联小程序 AppID |
| 小程序 AppID | 已注册并通过主体认证的小程序账号 |
| Node.js | >= 16.x（miniprogram-ci 依赖） |
| 云开发环境 | 已在微信开发者工具中开通云开发，获取环境 ID |
| 代码上传密钥 | 从微信公众平台下载，放在项目根目录 |

---

## 2. 一键发布流程（推荐）

### 2.1 自动发布脚本

```bash
python3.11 scripts/auto-release.py "版本描述"
```

**脚本自动完成以下步骤：**

| 步骤 | 操作 | 产物 |
|------|------|------|
| 1 | 检查前提条件 | 密钥文件、miniprogram-ci |
| 2 | 上传 8 个云函数 | 云函数部署到云端 |
| 3 | 上传前端代码 | 版本号自动递增 |
| 4 | 设置体验版 | 体验版可直接扫码访问 |
| 5 | 生成预览二维码 | `release/preview-qr.png` |
| 6 | 生成体验版二维码 | `release/experience-qr.png` |

### 2.2 使用示例

```bash
# 基本用法
python3.11 scripts/auto-release.py

# 带版本描述
python3.11 scripts/auto-release.py "feat(ui): 重新设计 UI 系统"

# 修复 bug
python3.11 scripts/auto-release.py "fix: 修复课时计算问题"
```

### 2.3 输出产物

```
release/
├── preview-qr.png      # 预览码（有效期短，适合开发调试）
└── experience-qr.png   # 体验码（有效期长，适合验收测试）
```

**扫码验收：**
- 用微信扫描 `preview-qr.png` → 预览最新代码
- 用微信扫描 `experience-qr.png` → 体验版（需先设置体验版）

---

## 3. 手动发布流程

如果自动脚本不可用，可按以下步骤手动操作。

### 3.1 上传云函数

**方式一：命令行（推荐）**

```bash
# 上传单个云函数
npx miniprogram-ci cloudfn \
  --pp /Volumes/macSdcard/AICoding/smart-hours \
  --appid wx73b9c9702f51e839 \
  --pkp /Volumes/macSdcard/AICoding/smart-hours/private.wx73b9c9702f51e839.key \
  --name course-manager

# 批量上传所有云函数
for func in init-db course-manager schedule-manager lesson-manager auto-deduct stats-query calendar-query audit-query; do
  npx miniprogram-ci cloudfn \
    --pp /Volumes/macSdcard/AICoding/smart-hours \
    --appid wx73b9c9702f51e839 \
    --pkp /Volumes/macSdcard/AICoding/smart-hours/private.wx73b9c9702f51e839.key \
    --name "$func"
done
```

**方式二：微信开发者工具**

1. 右键点击 `cloudfunctions` 目录
2. 选择「上传并部署：云端安装依赖」
3. 等待所有云函数上传完成

### 3.2 上传前端代码

```bash
npx miniprogram-ci upload \
  --pp /Volumes/macSdcard/AICoding/smart-hours \
  --appid wx73b9c9702f51e839 \
  --pkp /Volumes/macSdcard/AICoding/smart-hours/private.wx73b9c9702f51e839.key \
  --uv 1.0.19 \
  --ud "版本描述"
```

### 3.3 设置体验版

```bash
npx miniprogram-ci set-experience-version \
  --pp /Volumes/macSdcard/AICoding/smart-hours \
  --appid wx73b9c9702f51e839 \
  --pkp /Volumes/macSdcard/AICoding/smart-hours/private.wx73b9c9702f51e839.key \
  --uv 1.0.19
```

### 3.4 生成预览码

```bash
npx miniprogram-ci preview \
  --pp /Volumes/macSdcard/AICoding/smart-hours \
  --appid wx73b9c9702f51e839 \
  --pkp /Volumes/macSdcard/AICoding/smart-hours/private.wx73b9c9702f51e839.key \
  --uv 1.0.19 \
  --qrcode-format image \
  --qrcode-output-dest release/preview-qr.png
```

---

## 4. 云函数清单

| 云函数 | 用途 | 定时触发 |
|--------|------|---------|
| `init-db` | 数据库初始化（创建集合+索引） | 否 |
| `course-manager` | 课程增删改查 | 否 |
| `schedule-manager` | 排课管理 | 否 |
| `lesson-manager` | 手动消课 | 否 |
| `auto-deduct` | 自动消课 | ✅ 每 30 分钟 |
| `stats-query` | 统计查询 | 否 |
| `calendar-query` | 日历视图查询 | 否 |
| `audit-query` | 操作日志查询 | 否 |

---

## 5. 数据库初始化

首次使用需执行 `init-db` 云函数创建集合和索引。

### 5.1 执行方式

1. 在云开发控制台 → 云函数列表 → 找到 `init-db`
2. 点击「云端测试」
3. 不传参数，直接执行
4. 返回结果中确认集合创建成功

### 5.2 创建的集合

| 集合名 | 用途 | 主要索引 |
|--------|------|---------|
| `courses` | 课程信息 | `_openid+status`, `_openid+expiryDate` |
| `schedules` | 排课计划 | `courseId+status`, `dayOfWeek+time+status` |
| `lesson_records` | 消课记录 | `courseId+lessonDate`, `_openid+lessonDate` |
| `audit_logs` | 操作日志 | `_openid+createdAt`, `_openid+courseId+createdAt` |
| `deduction_locks` | 消课锁（幂等） | `lockKey` (UNIQUE), `expireAt` (TTL) |

---

## 6. 定时触发器配置

`auto-deduct` 需要定时触发器，每 30 分钟自动执行一次消课检查。

### 6.1 配置步骤

1. 云开发控制台 → 云函数列表 → `auto-deduct`
2. 点击函数名进入详情 → 「触发器」标签页
3. 点击「创建触发器」
4. 填写配置：
   - **触发方式**：定时触发
   - **Cron 表达式**：`0 */30 * * * * *`
5. 保存

### 6.2 验证

- 确认触发器状态为「启用」
- 可点击「立即执行」手动触发测试
- 查看云函数日志确认执行结果

> **安全说明**：`auto-deduct` 内置幂等控制（通过 `deduction_locks` 集合），同一课程同一天不会重复扣课。

---

## 7. 提交审核与发布

### 7.1 提交审核

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「管理」→「版本管理」
3. 在「开发版本」中找到刚上传的版本
4. 点击「提交审核」
5. 填写功能页面信息、类目信息
6. 提交后等待微信审核（通常 1-3 个工作日）

### 7.2 发布上线

审核通过后：
1. 在版本管理页面会显示「审核版本」
2. 点击「全量发布」即可上线
3. 也可选择「灰度发布」先小范围验证

---

## 8. 版本号管理

版本号记录在以下位置（自动同步）：

| 文件 | 字段 |
|------|------|
| `.version` | 纯文本版本号 |
| `project.config.json` | `version` 字段 |
| `miniprogram/app.js` | `globalData.version` 字段 |

自动发布脚本会自动递增 patch 版本号（如 `1.0.18` → `1.0.19`）。

---

## 9. 常见问题

### Q1: 云函数调用报错「云函数不存在」

**解决**：确认云函数已上传，且 `env.js` 中的环境 ID 正确。

### Q2: 自动发布脚本上传云函数失败

**解决**：检查网络连接，或手动逐个上传云函数。

### Q3: 预览码/体验码过期

**解决**：重新运行 `python3.11 scripts/auto-release.py` 生成新的二维码。

### Q4: 小程序审核不通过

**常见原因及对策**：

| 原因 | 对策 |
|------|------|
| 类目选择不当 | 选择「教育 → 在线教育」或「工具 → 信息查询」 |
| 功能页面不完整 | 确保每个 tab 页面都有实际内容 |
| 隐私协议 | 在设置页添加隐私协议说明 |

---

## 10. 上线检查清单

- [ ] 云开发环境 ID 配置正确（`env.js` + `app.js`）
- [ ] 8 个云函数全部上传成功
- [ ] 5 个数据库集合已创建且索引正确
- [ ] `auto-deduct` 定时触发器已启用（每 30 分钟）
- [ ] 手机端预览功能正常
- [ ] 小程序代码已上传并提交审核
- [ ] 审核通过后已点击发布
