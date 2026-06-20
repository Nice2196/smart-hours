@responsible MiMo-V2.5 Pro
@phase Phase 8

# Changelog

本项目所有重要变更均记录在此文件。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.0.12] - 2026-06-18

### Fixed

#### P0 — 核心功能修复（3 项）

- **Bug 3** 修复 `calendarQuery` 云函数未交叉校验课程表，导致已删除课程仍出现在日历中
- **Bug 7** 修复日历页面缺少 `onShow` 生命周期，切换月份后数据不刷新
- **Bug 9** 修复统计图表 echarts 实例检测逻辑，使用 `Object.keys` 长度区分真实 echarts 与 placeholder，避免零参数 `init()` 调用崩溃

#### P1 — UI/数据修复（7 项）

- **Bug 1** 修复排课页面星期复选框预计算状态错误，导致初始勾选显示不正确
- **Bug 4** 修复日历视图消课圆点不区分状态（已完成/待消课/已取消），同时修正消课类型标签显示
- **Bug 5** 修复 `courseTypeLabel` 映射缺失，导致课程类型显示为 undefined
- **Bug 6** 修复消课记录列表日期格式不统一，使用 `formatDate` 工具函数统一格式
- **Bug 10** 修复审计日志 action/trigger 映射标签缺失，操作类型和触发方式显示为原始代码
- **Bug 11** 替换已废弃的 `wx.getUserProfile` 接口，改用 `open-type="chooseAvatar"` 按钮 + `type="nickname"` 输入框获取用户头像和昵称
- **Bug 12** 修复统计页面预警图标显示异常

#### P2 — 样式修复（1 项）

- **Bug 2** 修复 7 个 WXSS 文件中文字溢出问题，统一添加 `text-overflow: ellipsis` 和 `word-break: break-all`

#### 其他

- 移除 `lesson/list.js` 中重复的 `formatDate()` 方法（已通过 utils/date 导入）
- 修复 `scripts/auto-release.py` 中 bare except 触发 ruff E722 警告

### Changed

- 统计图表组件 (`stats-chart`) echarts 检测改为基于 `Object.keys` 长度判断
- 设置页面 (`settings`) 用户头像获取方式改为微信原生组件
- `auto-release.py` bare except 改为 `except Exception`

---

## [1.0.0] - 2026-06-16

### Added

#### 云函数（8 个）

- `initDB` — 数据库初始化，自动创建 5 个集合及索引
- `courseManager` — 课程增删改查
- `scheduleManager` — 排课计划管理
- `lessonManager` — 手动消课
- `autoDeduct` — 自动消课（定时触发，内置幂等控制）
- `statsQuery` — 统计数据查询（课时消耗、费用统计等）
- `calendarQuery` — 日历视图数据查询
- `auditQuery` — 操作日志查询

#### 公共模块（5 个）

- `db` — 数据库连接与通用操作封装
- `auth` — 用户身份校验
- `idempotency` — 幂等性控制（防重复扣课）
- `constants` — 全局常量定义
- `logger` — 统一日志记录

#### 前端页面（9 个）

- 课程列表页 — 展示所有课程及状态
- 课程详情页 — 查看课程信息和消课历史
- 添加/编辑课程页 — 课程信息表单
- 排课管理页 — 设置每周固定上课时间
- 手动消课页 — 选择课程进行即时消课
- 日历视图页 — 按日期查看消课记录
- 统计图表页 — 课时消耗趋势和费用统计
- 操作日志页 — 查看全部操作记录
- 设置/个人中心页 — 用户信息和系统设置

#### 公共组件（5 个）

- 课程卡片组件 — 课程信息展示卡片
- 消课记录组件 — 单条消课记录展示
- 统计图表组件 — 数据可视化图表
- 日历组件 — 自定义日历控件
- 预警标签组件 — 低课时/即将过期提示

#### 核心功能

- **课程管理**：创建、编辑、删除课程，支持设置总课时、单价、有效期
- **排课管理**：为课程设置每周固定上课时间，支持多天排课
- **手动消课**：选择课程即时消课，支持选择日期
- **自动消课**：每 30 分钟定时触发，按排课计划自动消课，内置幂等控制防重复
- **日历视图**：按月展示消课记录，支持按日期查看详情
- **统计图表**：课时消耗趋势、课程排名、费用汇总
- **审计日志**：记录所有操作，支持按类型和时间筛选
- **预警机制**：低课时（<=3）和即将过期（7天内）自动提醒
