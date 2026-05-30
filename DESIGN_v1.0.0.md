# Kids-Star 儿童习惯养成系统 — 总体规划设计 v1.0.0

> **版本**: 1.0.0  
> **状态**: 设计阶段 / 待开发  
> **最后更新**: 2026-05-30

---

## 目录

1. [项目概述](#1-项目概述)
2. [用户角色与权限](#2-用户角色与权限)
3. [功能模块设计](#3-功能模块设计)
   - [3.1 功能全景图](#31-功能全景图)
   - [3.2 核心业务流程](#32-核心业务流程)
   - [3.3 任务维度定义](#33-任务维度定义)
   - [3.4 星星规则设计](#34-星星规则设计)
   - [3.5 星星兑换商店](#35-星星兑换商店)
   - [3.6 惩罚机制设计](#36-惩罚机制设计)
4. [技术架构](#4-技术架构)
5. [数据库设计](#5-数据库设计)
6. [API 设计概要](#6-api-设计概要)
7. [前端页面结构](#7-前端页面结构)
8. [Docker 容器化方案](#8-docker-容器化方案)
9. [安全设计](#9-安全设计)
10. [开发路线图](#10-开发路线图)
11. [附录：术语表](#11-附录术语表)

---

## 1. 项目概述

### 1.1 项目定位

Kids-Star 是一个面向多家庭的 SaaS 平台，帮助家长通过任务派发、星星奖惩、数据统计等手段，系统化地培养孩子良好的日常行为习惯和学习自律能力。覆盖小学至中学阶段（6-15 岁），家长以管理者角色主导，孩子作为任务的接收者和执行者参与。

**核心创新点**：任务体系分为「必修任务」和「挑战任务」两层。必修任务是孩子每天必须完成的基础项，由家长直接指派；挑战任务则由家长发布到"挑战广场"，孩子根据自己的兴趣和能力**主动领取**，完成后获得更高倍率星星。此外，孩子还可以**主动发起奖励申请**（如考试满分、获得表扬）和**提议自创任务**，经家长审核后获得星星或生成挑战任务。这种设计将"被动服从"转化为"主动争取"，培养孩子的自驱力。

### 1.2 核心价值

- **家长端**：一站式管理孩子的习惯养成计划，量化追踪成长轨迹，从数据中发现改进方向。
- **孩子端**：清晰看到「今天该做什么」，通过星星和奖励获得即时正向反馈，逐步建立自我管理意识。
- **平台端**：多家庭数据隔离，每个家庭是一个独立的数据空间。

### 1.3 设计原则

| 原则 | 说明 |
|------|------|
| 家庭即租户 | 每个家庭拥有完全独立的数据空间，数据不可跨家庭访问 |
| 移动优先 | 优先适配手机和平板，家长和孩子的主要使用场景在移动端 |
| 必修+挑战双轨 | 必修任务保障底线习惯，挑战任务激发主动性，孩子自主选择获取更高回报 |
| 孩子即主角 | 孩子不仅能执行任务，还能通过统一「发起申请」入口主动申请奖励或提议新任务，从被动执行者升级为主动管理者 |
| 正向激励为主 | 系统设计以奖励和成就感为核心驱动，惩罚机制作为辅助约束 |
| 渐进式复杂度 | 核心流程简单直观（3 步发任务、1 键打卡），高级功能按需展开 |

---

## 2. 用户角色与权限

### 2.1 角色定义

```
┌─────────────────────────────────────────────────────┐
│                    超级管理员 (Super Admin)            │
│                   平台级管理 / 运维                    │
├─────────────────────────────────────────────────────┤
│  家长 (Parent)          │     孩子 (Child)            │
│  · 家庭管理者            │     · 任务执行者             │
│  · 创建/管理任务         │     · 查看必修任务（必须完成） │
│  · 设置必修/挑战任务      │     · 浏览挑战广场并主动领取   │
│  · 审核任务完成          │     · 打卡/提交完成           │
│  · 设置奖惩规则          │     · 查看星星和奖励          │
│  · 查看统计数据          │     · 兑换奖励               │
│  · 管理家庭成员          │     · 查看个人统计            │
│                         │     · 发起申请（奖励/任务提议）  │
└─────────────────────────────────────────────────────┘
```

### 2.2 权限矩阵

| 功能模块 | Super Admin | Parent | Child |
|----------|:-----------:|:------:|:-----:|
| 平台运维管理 | ✓ | ✗ | ✗ |
| 创建/编辑家庭 | ✓ | ✓（仅自己） | ✗ |
| 邀请/管理家庭成员 | ✗ | ✓ | ✗ |
| 创建/编辑任务 | ✗ | ✓ | ✗ |
| 审核任务完成 | ✗ | ✓ | ✗ |
| 设置奖惩规则 | ✗ | ✓ | ✗ |
| 查看所有孩子统计 | ✗ | ✓ | ✗ |
| 接收/查看任务 | ✗ | ✗ | ✓（仅自己） |
| 打卡/提交任务 | ✗ | ✗ | ✓（仅自己） |
| 查看个人星星与统计 | ✗ | ✗ | ✓（仅自己） |
| 兑换奖励 | ✗ | ✗ | ✓（仅自己） |

---

## 3. 功能模块设计

### 3.1 功能全景图

```
Kids-Star
├── 1. 账户与家庭管理
│   ├── 1.1 注册/登录/密码找回
│   ├── 1.2 家庭创建与设置
│   ├── 1.3 家庭成员管理（添加/移除孩子）
│   └── 1.4 个人信息与偏好设置
│
├── 2. 任务管理（核心 — 家长端）
│   ├── 2.1 任务模板库（预设常用任务，区分必修/挑战）
│   ├── 2.2 创建必修任务（直接指派给孩子，必须完成）
│   ├── 2.3 发布挑战任务（投放到挑战广场，孩子自主领取）
│   ├── 2.4 任务类型切换（必修 ⇄ 挑战）
│   ├── 2.5 任务编辑/暂停/删除
│   ├── 2.6 任务分类与标签
│   └── 2.7 任务到期/逾期提醒
│
├── 3. 任务执行（孩子端）
│   ├── 3.1 必修任务列表（今日必须完成的事项）
│   ├── 3.2 挑战广场（浏览并领取感兴趣的挑战任务）
│   ├── 3.3 我的挑战（已领取的挑战任务列表）
│   ├── 3.4 打卡/提交完成（支持拍照上传）
│   ├── 3.5 任务进度追踪
│   ├── 3.6 任务日历视图
│   └── 3.7 发起申请（统一入口：已完成成就申请星星 / 提议新任务申请星星）
│
├── 4. 审核与反馈
│   ├── 4.1 任务完成审核（打卡审核）
│   ├── 4.2 孩子申请审核（统一入口，按类型分流：奖励申请→直接发星 / 任务提议→生成挑战任务）
│   ├── 4.3 通过/驳回（支持评语 + 调整星星数量）
│   ├── 4.4 批量审核
│   └── 4.5 审核记录历史
│
├── 5. 奖惩机制
│   ├── 5.1 星星规则配置（必修星星/挑战倍率）
│   ├── 5.2 惩罚规则配置（三层：任务内嵌 / 家庭规则 / 手动惩罚）
│   ├── 5.3 星星兑换商店（商品卡片内置兑换按钮 → 一键申请 → 家长审核 → 扣星）
│   ├── 5.4 奖励物品管理（家长自定义商店商品）
│   ├── 5.5 兑换记录
│   ├── 5.6 孩子申请管理（统一处理奖励申请和任务提议的审核）
│   └── 5.7 成就徽章系统（含挑战达人专属徽章）
│
├── 6. 数据统计
│   ├── 6.1 孩子维度统计（必修完成率/挑战参与度/星星变化/惩罚记录）
│   ├── 6.2 任务维度统计（最常完成/挑战热度/最容易逾期）
│   ├── 6.3 时间维度统计（日/周/月/学期）
│   ├── 6.4 家庭综合报告
│   └── 6.5 数据导出（PDF / CSV）
│
└── 7. 消息与通知
    ├── 7.1 新必修任务通知
    ├── 7.2 挑战广场上新通知
└── 7. 消息与通知
    ├── 7.1 新必修任务通知
    ├── 7.2 挑战广场上新通知
    ├── 7.3 审核结果通知（打卡/申请审批/兑换审批）
    ├── 7.4 兑换申请状态通知
    ├── 7.5 惩罚通知（自动惩罚/手动扣星，附原因）
    └── 7.6 提醒通知（逾期/即将到期）
```

#### 通知机制说明

| 维度 | 方案 |
|------|------|
| **站内通知** | 主要渠道。顶部导航栏未读徽标 + 通知列表页。支持按类型筛选、标记已读、批量已读 |
| **推送通知** | PWA 支持时启用浏览器推送（Phase 3）；原生 App 推送（Phase 5） |
| **邮件通知** | 仅用于密码重置、账户安全等关键场景；日常任务通知不走邮件（避免骚扰） |
| **通知频率** | 实时推送审核结果和惩罚通知；每日定时汇总推送今日任务清单（早8点，可配置） |
| **存储** | notifications 表，关键字段：user_id, type, title, body, is_read, related_id（关联业务ID）, created_at |

> **设计原则**：通知不轰炸。日常任务提醒以站内为主，紧急和关键通知走实时推送。所有通知 30 天后自动归档。

### 3.2 核心业务流程

#### 3.2.1 必修任务生命周期

```
家长创建必修任务 ──→ 直接指派给孩子 ──→ 孩子收到通知
                                            │
                                            ▼
                                      孩子执行并打卡
                                            │
                                            ▼
                                      家长审核 ◄── 驳回（可附评语）
                                            │
                                      通过 ▼
                                      星星自动发放
                                      任务标记完成
                                      
                              （如逾期未完成 → 可能扣星）
```

#### 3.2.2 挑战任务生命周期

```
家长发布挑战任务 ──→ 投放到挑战广场 ──→ 孩子浏览发现
                                            │
                                    孩子主动领取 ◄── 不感兴趣可忽略
                                            │
                                    任务进入「我的挑战」
                                            │
                                      孩子执行并打卡
                                            │
                                            ▼
                                      家长审核 ◄── 驳回（可附评语）
                                            │
                                      通过 ▼
                              高倍率星星发放（1.5x ~ 3x）
                              任务标记完成
                              
                              （逾期未完成 → 不扣星，仅标记失败）
```

#### 3.2.3 两种任务对比

| 维度 | 必修任务 | 挑战任务 |
|------|---------|---------|
| 指派方式 | 家长直接分配，孩子被动接收 | 家长发布到广场，孩子主动领取 |
| 完成要求 | 必须完成 | 自愿选择 |
| 星星回报 | 基础星星（1x） | 高倍率星星（1.5x ~ 3x） |
| 逾期惩罚 | 可配置扣星 | 不扣星，仅标记失败 |
| 领取上限 | 无（家长控制数量） | 可设置每周领取上限 |
| 设计意图 | 保障底线习惯 | 激发自驱力与探索欲 |

#### 3.2.4 星星流转

```
任务完成 ──→ 家长审核通过 ──→ 星星入账（孩子账户）
奖励申请 ──→ 家长审核通过 ──→ 星星入账（孩子账户）
                 │                    │
                 │            （必修=基础星星）
                 │            （挑战=基础星星 × 倍率）
                 │            （奖励申请=家长指定数量）
                 │                    │
                 │      孩子申请兑换 ◄──┘
                 │           │
                 │    家长审核兑换申请
                 │           │
                 │      通过 ▼
                 │      星星扣除
                 │      兑换记录留存
                 │      通知家长
                 │
           驳回 ▼
          0 星星，可重新提交
```


#### 3.2.5 孩子发起申请（统一入口）

孩子有一个统一的「发起申请」入口，根据申请类型自动分流：

```
孩子打开「发起申请」页面
            │
    选择申请类型
            │
   ┌────────┴────────┐
   │                 │
   ▼                 ▼
申请奖励            提议任务
(已完成的事)        (想做的事)
   │                 │
   │                 │
   ▼                 ▼
填写：             填写：
· 申请理由          · 任务名称
· 上传证据截图      · 任务描述
· 申请星星数        · 任务分类
   │               · 申请星星数
   │               · 建议完成时间
   │                 │
   └────────┬────────┘
            │
            ▼
      家长收到审核通知
            │
     ┌──────┴──────┐
     │             │
  通过 ▼        驳回 ▼
     │             │
  ┌──┴──┐      附驳回理由
  │     │      可建议修正
  ▼     ▼
奖励申请  任务提议
  │     │
  ▼     ▼
直接发星  自动生成
到孩子    挑战任务
账户      (绑定孩子)
  │     │
  └──┬──┘
     ▼
  孩子收到通知
```

> **设计要点**：虽然前端入口统一，但后端根据 `request_type` 分流处理。奖励申请（已完成成就）审批通过后直接发星；任务提议（未来任务）审批通过后生成挑战任务，星星需等任务完成后才发放。这样既简化了孩子的操作路径，又保持了业务逻辑的清晰。

### 3.3 任务维度定义

每个任务同时具备两个维度的属性：

**维度一：内容类型（task_type）**

| 类型 | 说明 | 示例 |
|------|------|------|
| **每日习惯** | 每天需完成的固定行为 | 刷牙、整理书包、阅读 30 分钟 |
| **学习作业** | 学习相关的任务 | 完成数学练习册 P20-25、背诵课文 |
| **家务劳动** | 家务相关的任务 | 洗碗、扫地、倒垃圾 |
| **自定义任务** | 家长自由定义的任务 | 练习钢琴 1 小时、户外运动 |

**维度二：难度模式（difficulty）**

| 模式 | 说明 | 星星倍率 | 惩罚 | 孩子操作 |
|------|------|:------:|------|----------|
| **必修 (required)** | 家长指派，必须完成 | 1x | 逾期可扣星 | 被动接收 → 执行 → 打卡 |
| **挑战 (challenge)** | 家长发布到广场，孩子自主领取 | 1.5x ~ 3x | 不扣星 | 浏览 → 主动领取 → 执行 → 打卡 |

> **设计要点**：同一内容类型的任务，家长可以灵活设定为必修或挑战。比如「背诵课文」作为日常作业可设为必修（1x 星星），而「背诵一篇额外古文」可作为挑战发布（2x 星星），激励孩子扩展学习边界。

### 3.4 星星规则设计

```
┌──────────────────────────────────────────────────────┐
│           星星规则（家长可自定义）                       │
├──────────────────────────────────────────────────────┤
│  必修任务星星                                          │
│  · 按时完成：+N 星（基础星星）                          │
│  · 提前完成：+N + 额外奖励星                            │
│  · 逾期完成：+N × 50%（打折）                          │
│  · 未完成：  -M 星（可选启用）                          │
├──────────────────────────────────────────────────────┤
│  挑战任务星星                                          │
│  · 按时完成：+N × 倍率（家长设定 1.5x ~ 3x）            │
│  · 提前完成：+N × 倍率 + 额外奖励                       │
│  · 逾期完成：+N × 倍率 × 50%                           │
│  · 未完成：  不扣星（保护挑战积极性）                     │
│  · 领取后放弃：可设置惩罚（如本周禁止领取新挑战）           │
├──────────────────────────────────────────────────────┤
│  额外奖励（两种任务通用）                                │
│  · 连续 7 天全勤（必修）：额外 +X 星                     │
│  · 月度必修全勤：额外 +Y 星 + 全勤徽章                   │
│  · 月度挑战完成 ≥ N 个：额外 +Z 星 + 挑战达人徽章         │
│  · 家长特别表扬：手动加星                                │
├──────────────────────────────────────────────────────┤
│  挑战领取限制（可选，防止过度）                           │
│  · 每周最多领取 N 个挑战任务                             │
│  · 同时进行中的挑战不超过 M 个                           │
│  · 挑战任务领取后 N 小时内必须开始（防占坑）              │
└──────────────────────────────────────────────────────┘
```

### 3.5 星星兑换商店

```
┌──────────────────────────────────────────────────────┐
│                 星星兑换商店流程                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  家长端                    孩子端                       │
│  ┌──────────┐            ┌──────────────────┐         │
│  │ 创建奖励  │            │ 浏览商店（卡片网格）│         │
│  │ · 名称    │  发布到    │ ┌──────┐┌──────┐ │         │
│  │ · 描述    │ ────────→ │ │ 奖品A ││ 奖品B │ │         │
│  │ · 图片    │  商店中    │ │ ⭐50  ││ ⭐100 │ │         │
│  │ · 星价    │            │ │[兑换]││[兑换]│ │         │
│  │ · 库存    │            │ └──────┘└──────┘ │         │
│  └──────────┘            └────────┬─────────┘         │
│                                   │                   │
│                         点击卡片上的「兑换」             │
│                                   │                   │
│                     ┌─────────────▼─────────────┐      │
│                     │   兑换申请已提交            │      │
│                     │   状态：待家长审核          │      │
│                     └─────────────┬─────────────┘      │
│                                   │                   │
│  ┌──────────────┐                │                   │
│  │ 家长审核兑换  │ ◄─────────────┘                   │
│  │ · 查看申请    │                                    │
│  │ · 通过/驳回   │                                    │
│  │ · 附评语     │                                    │
│  └──────┬───────┘                                    │
│         │                                            │
│    ┌────┴────┐                                       │
│    │         │                                       │
│  通过 ▼    驳回 ▼                                     │
│  · 扣除星星  · 附驳回理由                              │
│  · 标记已兑现 · 星星不变                               │
│  · 通知孩子  · 通知孩子                                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

> **设计要点**：兑换不是即时的——孩子发起兑换申请后，必须经过家长审核。这样做的好处是：(1) 家长可以控制孩子兑换的物品是否合适；(2) 实物奖励需要家长实际兑现，审核环节确保家长知晓并同意；(3) 家长可以在审核时附加鼓励或引导性评语。

### 3.6 惩罚机制设计

惩罚机制分为三个层次，从自动化到人工干预，由轻到重：

```
┌──────────────────────────────────────────────────────┐
│              惩罚机制三层架构                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  第一层：任务内嵌惩罚（自动执行，可逐任务配置）            │
│  ┌────────────────────────────────────────────┐      │
│  │  场景                │  惩罚                │      │
│  ├──────────────────────┼─────────────────────│      │
│  │  必修任务逾期完成      │  星星打折 50%        │      │
│  │  必修任务未完成        │  扣除 N 星（家长设定） │      │
│  │  挑战任务逾期完成      │  星星打折 50%        │      │
│  │  挑战任务未完成        │  不扣星（保护积极性）  │      │
│  │  挑战任务领取后放弃     │  冷却期（N天内禁领）  │      │
│  └────────────────────────────────────────────┘      │
│                                                      │
│  第二层：家庭规则惩罚（家长配置阈值，自动触发）            │
│  ┌────────────────────────────────────────────┐      │
│  │  规则                │  触发条件 & 惩罚      │      │
│  ├──────────────────────┼─────────────────────│      │
│  │  连续未完成警戒        │  连续 N 天必修未完成   │      │
│  │                       │  → 额外扣 Y 星       │      │
│  │  周度最低完成率        │  本周完成率 < X%      │      │
│  │                       │  → 限制兑换商店 N 天  │      │
│  │  挑战滥用防护          │  本周领取 ≥ N 个但     │      │
│  │                       │  完成率 < 50%        │      │
│  │                       │  → 下周禁止领取挑战   │      │
│  └────────────────────────────────────────────┘      │
│                                                      │
│  第三层：家长手动惩罚（人工触发，附原因）                  │
│  ┌────────────────────────────────────────────┐      │
│  │  · 家长在任意时候可手动扣星                    │      │
│  │  · 必须填写惩罚原因（孩子可见）                 │      │
│  │  · 可选附带"改正建议"                         │      │
│  │  · 记录到星星流水，标注 manual_penalty 类型    │      │
│  │  · 孩子端收到通知并显示原因                    │      │
│  └────────────────────────────────────────────┘      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### 3.6.1 惩罚设计原则

| 原则 | 说明 |
|------|------|
| **可预期** | 所有惩罚规则对孩子透明可见，不是家长"随心所欲" |
| **有上限** | 单日扣星不超过家庭设定的上限，防止一次打击过大 |
| **带原因** | 每条惩罚记录必须附带原因，孩子能理解为什么被扣星 |
| **可补救** | 鼓励设计"补救任务"——完成额外任务可抵消惩罚（家长可选启用） |
| **正向为主** | 惩罚永远不能让孩子星星余额变负，最低为 0（保护基本尊严） |

#### 3.6.2 惩罚与任务的关系

惩罚**不独立于任务存在**——它不是单独的一个"惩罚模块"，而是嵌入在任务体系的各个环节中：

- **任务创建时**：家长设定该任务的惩罚参数（是否允许扣星、扣多少）
- **任务审核时**：系统根据任务配置自动计算惩罚（逾期打折、未完成扣星）
- **家庭设置中**：家长配置全局惩罚规则（连续未完成阈值、周完成率底线）
- **日常管理中**：家长可随时手动扣星（严重违规、原则性问题）

> **核心理念**：惩罚的目的是让孩子理解"选择有后果"，而非制造恐惧。因此设计上：(1) 挑战任务不设惩罚，保护探索欲；(2) 所有规则提前告知；(3) 提供补救路径；(4) 星星永不为负。

---

## 4. 技术架构

### 4.1 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| **后端框架** | Python FastAPI | 异步高性能、自动 OpenAPI 文档、类型安全、轻量 |
| **前端框架** | Vue 3 + TypeScript | 渐进式、学习曲线平缓、组合式 API 灵活 |
| **前端构建** | Vite | 极速冷启动、HMR 热更新 |
| **UI 组件库** | PrimeVue / Naive UI | 移动端友好、组件丰富 |
| **数据库** | PostgreSQL 15+ | 强大的 JSON 支持、窗口函数适合统计分析、ACID |
| **缓存** | Redis 7+ | 会话存储、频率限制、任务队列 |
| **任务队列** | Celery + Redis | 异步通知、定时提醒、数据统计计算 |
| **文件存储** | MinIO (S3 兼容) | 孩子打卡拍照上传、头像等 |
| **反向代理** | Nginx | 静态资源、SSL 终结、负载均衡 |
| **容器化** | Docker + Docker Compose | 一键部署、环境一致 |

### 4.2 架构图

```
                              ┌──────────────┐
                              │   Nginx      │
                              │  (反向代理)    │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
              │  Frontend  │   │  Backend   │   │   MinIO   │
              │  (Vue 3)   │   │ (FastAPI)  │   │ (文件存储)  │
              │  Static    │   │  API:8000  │   │  :9000    │
              └───────────┘   └─────┬──────┘   └───────────┘
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                   ┌─────▼─────┐ ┌──▼────┐ ┌──▼──────┐
                   │ PostgreSQL │ │ Redis │ │ Celery  │
                   │   :5432    │ │ :6379 │ │ Worker  │
                   └───────────┘ └───────┘ └─────────┘
```

### 4.3 后端项目结构

```
backend/
├── app/
│   ├── api/                    # API 路由层
│   │   ├── v1/
│   │   │   ├── auth.py         # 认证相关接口
│   │   │   ├── families.py     # 家庭管理接口
│   │   │   ├── tasks.py        # 任务管理接口
│   │   │   ├── submissions.py  # 任务提交/审核接口
│   │   │   ├── requests.py    # 孩子申请接口（奖励申请 + 任务提议统一入口）
│   │   │   ├── rewards.py      # 奖励与兑换接口
│   │   │   ├── penalties.py    # 惩罚规则与手动扣星接口
│   │   │   ├── statistics.py   # 统计接口
│   │   │   └── notifications.py # 通知接口
│   │   └── deps.py             # 依赖注入（认证、数据库会话等）
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # JWT / 密码哈希
│   │   └── database.py         # 数据库连接与会话
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── task.py
│   │   ├── submission.py
│   │   └── reward.py
│   ├── schemas/                # Pydantic 请求/响应模型
│   ├── services/               # 业务逻辑层
│   │   ├── task_service.py
│   │   ├── points_service.py
│   │   ├── penalty_service.py   # 惩罚规则评估与执行
│   │   ├── notification_service.py # 站内通知与推送
│   │   └── statistics_service.py
│   ├── tasks/                  # Celery 异步任务
│   │   ├── notifications.py    # 通知推送（新任务/审核结果/提醒）
│   │   ├── reminders.py        # 定时提醒（逾期/即将到期）
│   │   ├── streaks.py          # 连续打卡检查与徽章发放
│   │   └── penalties.py        # 家庭惩罚规则定期评估
│   └── utils/
├── alembic/                    # 数据库迁移
├── tests/
├── Dockerfile
├── requirements.txt
└── main.py                     # 应用入口
```

### 4.4 前端项目结构

```
frontend/
├── src/
│   ├── views/                  # 页面组件
│   │   ├── auth/               # 登录/注册
│   │   ├── parent/             # 家长端页面
│   │   │   ├── Dashboard.vue
│   │   │   ├── TaskManage.vue
│   │   │   ├── ReviewCenter.vue
│   │   │   ├── RewardManage.vue
│   │   │   ├── PenaltyManage.vue
│   │   │   ├── Statistics.vue
│   │   │   └── FamilySettings.vue
│   │   └── child/              # 孩子端页面
│   │       ├── MyTasks.vue
│   │       ├── ChallengeBoard.vue
│   │       ├── MyChallenges.vue
│   │       ├── SubmitRequest.vue
│   │       ├── MyPoints.vue
│   │       ├── RewardShop.vue
│   │       └── MyStats.vue
│   ├── components/             # 通用组件
│   ├── composables/            # 组合式函数（状态管理）
│   ├── router/                 # 路由配置
│   ├── stores/                 # Pinia 状态管理
│   ├── api/                    # API 请求封装
│   ├── types/                  # TypeScript 类型定义
│   └── assets/
├── Dockerfile
├── package.json
└── vite.config.ts
```

---

## 5. 数据库设计

### 5.1 ER 图（核心实体）

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│   User   │       │    Family    │       │  Child   │
├──────────┤       ├──────────────┤       ├──────────┤
│ id (PK)  │───┬───│ id (PK)      │───┬───│ id (PK)  │
│ email    │   │   │ name         │   │   │ user_id  │
│ password │   │   │ invite_code  │   │   │ family_id│
│ name     │   │   │ created_at   │   │   │ nickname │
│ role     │   │   └──────────────┘   │   │ avatar   │
│ avatar   │   │                      │   │ points   │
└──────────┘   │                      │   └──────────┘
               │                      │
      ┌────────┘               ┌──────┘
      │                        │
      │  ┌─────────────────┐   │
      │  │ FamilyMember    │   │
      │  ├─────────────────┤   │
      └──│ user_id  (FK)   │   │
         │ family_id (FK)  │───┘
         │ role (parent/   │
         │   child)        │
         └─────────────────┘


┌──────────┐       ┌──────────────┐       ┌──────────────┐
│   Task   │       │  Submission  │       │   Reward     │
├──────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)  │──┬────│ id (PK)      │       │ id (PK)      │
│ family_id│  │    │ task_id (FK) │       │ family_id    │
│ title    │  │    │ child_id(FK) │       │ name         │
│ desc     │  │    │ status       │       │ description  │
│ task_type│  │    │ photo_urls   │       │ points_cost  │
│ difficulty│ │    │ child_note   │       │ image_url    │
│ base_pts │  │    │ parent_note  │       │ stock        │
│ challenge│  │    │ points_earned│       │ is_active    │
│ _multiplier│  │   │ reviewed_by  │       └──────────────┘
│ category │  │    │ submitted_at │
│ repeat   │  │    │ reviewed_at  │
│ assignee │──┘    └──────────────┘
│ due_date │
│ status   │
│ created_by│
│ claim_limit│       ┌──────────────┐
│ claim_deadline│    │TaskClaim     │
└──────────┘       ├──────────────┤
                   │ id (PK)      │
                   │ task_id (FK) │
                   │ child_id(FK) │
                   │ status       │
                   │ claimed_at   │
                   │ completed_at │
                   └──────────────┘

┌──────────────┐       ┌──────────────┐
│PointsRecord  │       │  Redemption  │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ child_id(FK) │       │ child_id(FK) │
│ task_id (FK) │       │ reward_id(FK)│
│ amount       │       │ points_spent │
│ type         │       │ status       │
│ reason       │       │ parent_note  │
│ created_at   │       │ reviewed_by  │
└──────────────┘       │ redeemed_at  │
                       │ reviewed_at  │
┌──────────────────┐   │ fulfilled_at │
│RewardApplication │   └──────────────┘
├──────────────────┤
│ id (PK)          │   ┌──────────────────┐
│ family_id (FK)   │   │ FamilyPenaltyRule│
│ child_id (FK)    │   ├──────────────────┤
│ title            │   │ id (PK)          │
│ photo_urls       │   │ family_id (FK)   │
│ points_requested │   │ rule_type        │
│ points_granted   │   │ trigger_config   │
│ status           │   │ penalty_action   │
│ parent_note      │   │ is_enabled       │
│ submitted_at     │   └──────────────────┘
│ reviewed_at      │
└──────────────────┘   ┌──────────────────┐
                       │  TaskProposal    │
┌──────────────┐       ├──────────────────┤
│  TaskClaim   │       │ id (PK)          │
├──────────────┤       │ family_id (FK)   │
│ id (PK)      │       │ child_id (FK)    │
│ task_id (FK) │       │ title            │
│ child_id(FK) │       │ points_requested │
│ status       │       │ points_approved  │
│ claimed_at   │       │ status           │
│ completed_at │       │ created_task_id  │
└──────────────┘       │ submitted_at     │
                       │ reviewed_at      │
                       └──────────────────┘
```

### 5.2 核心表定义

```sql
-- 用户表（平台级，不绑定家庭）
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name          VARCHAR(100) NOT NULL,
    role          VARCHAR(20) NOT NULL DEFAULT 'parent',  -- 'parent' | 'child' | 'admin'
    avatar_url    VARCHAR(500),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 家庭表（租户隔离核心）
CREATE TABLE families (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    invite_code     VARCHAR(20) UNIQUE NOT NULL,
    max_daily_penalty INTEGER DEFAULT 20,   -- 家庭级：单日扣星上限（防过度惩罚）
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 家庭成员关联表
CREATE TABLE family_members (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id),
    family_id  UUID NOT NULL REFERENCES families(id),
    role       VARCHAR(20) NOT NULL DEFAULT 'child',  -- 'parent' | 'child'
    nickname   VARCHAR(50),       -- 孩子在家庭中的昵称
    avatar_url VARCHAR(500),
    points     INTEGER DEFAULT 0, -- 孩子当前星星余额
    joined_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, family_id)
);

-- 任务表
CREATE TABLE tasks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id           UUID NOT NULL REFERENCES families(id),
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    task_type           VARCHAR(30) NOT NULL DEFAULT 'custom',  -- 'daily_habit' | 'homework' | 'chore' | 'custom'
    difficulty          VARCHAR(20) NOT NULL DEFAULT 'required', -- 'required'(必修) | 'challenge'(挑战)
    category            VARCHAR(50),          -- 自定义分类标签
    base_points         INTEGER NOT NULL DEFAULT 5,
    challenge_multiplier DECIMAL(2,1) DEFAULT 1.5,  -- 挑战倍率 1.5 ~ 3.0（仅 difficulty='challenge' 时生效）
    bonus_points        INTEGER DEFAULT 0,    -- 提前完成额外奖励
    penalty_points      INTEGER DEFAULT 0,    -- 未完成扣除星数（挑战任务强制为 0）
    allow_overtime_discount BOOLEAN DEFAULT TRUE, -- 是否允许逾期打折（关闭则逾期=0星）
    repeat_type         VARCHAR(20) DEFAULT 'once',  -- 'once' | 'daily' | 'weekly' | 'monthly'
    repeat_config       JSONB,               -- {"days_of_week":[1,3,5]} 等重复配置
    due_date            DATE,                -- 截止日期
    due_time            TIME,                -- 截止时间（如 21:00）
    assigned_to         UUID[] NOT NULL,      -- 必修任务：指派的孩子 user_id 数组；挑战任务：可为空（面向全家庭）
    claim_limit         INTEGER DEFAULT 0,    -- 挑战任务：最多被几人领取（0=不限）
    claim_deadline_hours INTEGER DEFAULT 48,  -- 挑战任务：领取后多少小时内必须完成
    status              VARCHAR(20) DEFAULT 'active',  -- 'active' | 'paused' | 'completed' | 'cancelled'
    created_by          UUID NOT NULL REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 挑战任务领取记录表
CREATE TABLE task_claims (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      UUID NOT NULL REFERENCES tasks(id),
    child_id     UUID NOT NULL REFERENCES users(id),
    status       VARCHAR(20) DEFAULT 'claimed',  -- 'claimed' | 'in_progress' | 'completed' | 'abandoned'
    claimed_at   TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE(task_id, child_id)  -- 同一孩子不能重复领取同一挑战
);

-- 任务提交表
CREATE TABLE submissions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      UUID NOT NULL REFERENCES tasks(id),
    child_id     UUID NOT NULL REFERENCES users(id),
    status       VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'approved' | 'rejected'
    photo_urls   TEXT[],              -- 打卡拍照
    child_note   TEXT,                -- 孩子备注
    parent_note  TEXT,                -- 家长审核评语
    points_earned INTEGER DEFAULT 0,  -- 实际获得星星
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_by  UUID REFERENCES users(id),
    reviewed_at  TIMESTAMPTZ
);

-- 星星流水表
CREATE TABLE points_records (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id   UUID NOT NULL REFERENCES users(id),
    task_id    UUID REFERENCES tasks(id),
    amount     INTEGER NOT NULL,      -- 正数=获得，负数=扣除
    type       VARCHAR(20) NOT NULL,  -- 'task_complete' | 'bonus' | 'auto_penalty' | 'manual_penalty' | 'redemption' | 'reward_application' | 'manual'
    reason     VARCHAR(300),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 奖励物品表
CREATE TABLE rewards (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id    UUID NOT NULL REFERENCES families(id),
    name         VARCHAR(100) NOT NULL,
    description  TEXT,
    points_cost  INTEGER NOT NULL,                  -- 兑换所需星星数
    image_url    VARCHAR(500),
    stock        INTEGER DEFAULT -1,  -- -1 = 不限量
    is_active    BOOLEAN DEFAULT TRUE,
    created_by   UUID NOT NULL REFERENCES users(id),
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 兑换记录表
CREATE TABLE redemptions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id      UUID NOT NULL REFERENCES users(id),
    reward_id     UUID NOT NULL REFERENCES rewards(id),
    points_spent  INTEGER NOT NULL,
    status        VARCHAR(20) DEFAULT 'pending', -- 'pending' | 'approved' | 'fulfilled' | 'rejected'
    parent_note   TEXT,                -- 家长审核评语
    reviewed_by   UUID REFERENCES users(id),
    redeemed_at   TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at   TIMESTAMPTZ,
    fulfilled_at  TIMESTAMPTZ
);

-- 成就徽章表
CREATE TABLE badges (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id   UUID NOT NULL REFERENCES families(id),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url    VARCHAR(500),
    condition   JSONB NOT NULL,       -- {"type":"streak","days":7} 触发条件
    created_by  UUID NOT NULL REFERENCES users(id)
);

-- 家庭惩罚规则表
CREATE TABLE family_penalty_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    rule_type       VARCHAR(30) NOT NULL,     -- 'streak_penalty' | 'weekly_completion' | 'challenge_abuse'
    name            VARCHAR(100) NOT NULL,    -- 规则名称（如"连续3天未完成惩罚"）
    is_enabled      BOOLEAN DEFAULT TRUE,
    trigger_config  JSONB NOT NULL,           -- 触发条件 {"consecutive_days":3}
    penalty_action  JSONB NOT NULL,           -- 惩罚动作 {"deduct_stars":10, "restrict_shop_days":2}
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 孩子徽章关联表
CREATE TABLE child_badges (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id   UUID NOT NULL REFERENCES users(id),
    badge_id   UUID NOT NULL REFERENCES badges(id),
    earned_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(child_id, badge_id)
);

-- 奖励申请表（孩子主动发起）
CREATE TABLE reward_applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    child_id        UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(200) NOT NULL,      -- 如"期末考试数学100分"
    description     TEXT,                        -- 详细说明
    photo_urls      TEXT[],                      -- 证据截图（成绩单/表扬信等）
    points_requested INTEGER NOT NULL,           -- 孩子申请的星星数
    points_granted  INTEGER,                    -- 家长实际发放的星星数（可调整）
    status          VARCHAR(20) DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected'
    parent_note     TEXT,                        -- 家长评语
    reviewed_by     UUID REFERENCES users(id),
    submitted_at    TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ
);

-- 任务申请表（孩子提议自定义挑战任务）
CREATE TABLE task_proposals (

-- 通知表
CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    type        VARCHAR(30) NOT NULL,  -- 'new_task' | 'challenge_new' | 'review_result' | 'redemption_update' | 'penalty' | 'reminder'
    title       VARCHAR(200) NOT NULL,
    body        TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    related_id  UUID,                  -- 关联的业务 ID（task/submission/request 等）
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read, created_at DESC);
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    child_id        UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(200) NOT NULL,      -- 提议的任务名称
    description     TEXT,                        -- 任务描述
    category        VARCHAR(50),                 -- 任务分类
    points_requested INTEGER NOT NULL,           -- 申请的星星数
    points_approved INTEGER,                    -- 家长批准的星星数
    multiplier_approved DECIMAL(2,1) DEFAULT 1.5, -- 家长批准的倍率
    due_date        DATE,                        -- 建议的完成日期
    status          VARCHAR(20) DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected'
    parent_note     TEXT,                        -- 家长评语
    created_task_id UUID REFERENCES tasks(id),  -- 通过后自动生成的挑战任务 ID
    reviewed_by     UUID REFERENCES users(id),
    submitted_at    TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ
);
```

---

## 6. API 设计概要

### 6.1 API 规范

- **风格**: RESTful
- **版本**: `/api/v1/`
- **认证**: JWT Bearer Token（Access Token 2h + Refresh Token 7d）
- **文档**: 自动生成 Swagger UI (`/docs`) 和 ReDoc (`/redoc`)
- **响应格式**:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 6.2 API 端点一览

```
认证模块 (Auth)
├── POST   /api/v1/auth/register          # 家长注册
├── POST   /api/v1/auth/login             # 登录
├── POST   /api/v1/auth/refresh           # 刷新 Token
├── POST   /api/v1/auth/logout            # 登出
└── POST   /api/v1/auth/forgot-password   # 忘记密码

家庭管理 (Families)
├── POST   /api/v1/families               # 创建家庭
├── GET    /api/v1/families/{id}          # 获取家庭信息
├── PUT    /api/v1/families/{id}          # 更新家庭设置
├── POST   /api/v1/families/{id}/members  # 添加成员（孩子）
├── GET    /api/v1/families/{id}/members  # 成员列表
├── PUT    /api/v1/families/{id}/members/{mid}  # 更新成员信息
├── DELETE /api/v1/families/{id}/members/{mid}  # 移除成员
└── POST   /api/v1/families/join          # 通过邀请码加入

惩罚管理 (Penalty Rules) [家长端]
├── GET    /api/v1/families/{id}/penalty-rules    # 家庭惩罚规则列表
├── POST   /api/v1/families/{id}/penalty-rules    # 创建惩罚规则
├── PUT    /api/v1/penalty-rules/{id}             # 编辑惩罚规则
├── DELETE /api/v1/penalty-rules/{id}             # 删除惩罚规则
├── PATCH  /api/v1/penalty-rules/{id}/toggle      # 启用/禁用规则
├── POST   /api/v1/children/{id}/manual-penalty   # 家长手动扣星（附原因）
└── GET    /api/v1/children/{id}/penalty-history  # 孩子惩罚记录

任务管理 (Tasks) [家长端]
├── GET    /api/v1/tasks                  # 任务列表（筛选：difficulty/状态/孩子/类型）
├── POST   /api/v1/tasks                  # 创建任务（可指定必修/挑战）
├── GET    /api/v1/tasks/{id}             # 任务详情
├── PUT    /api/v1/tasks/{id}             # 编辑任务
├── DELETE /api/v1/tasks/{id}             # 删除任务
├── PATCH  /api/v1/tasks/{id}/status      # 变更任务状态
├── PATCH  /api/v1/tasks/{id}/difficulty  # 切换必修 ⇄ 挑战模式
└── GET    /api/v1/tasks/templates        # 获取任务模板

任务执行 (Tasks) [孩子端]
├── GET    /api/v1/my-tasks               # 我的必修任务（今日/全部）
├── GET    /api/v1/my-tasks/{id}          # 任务详情
├── POST   /api/v1/my-tasks/{id}/submit   # 提交/打卡
├── GET    /api/v1/challenge-board        # 挑战广场（可领取的挑战列表）
├── POST   /api/v1/challenge-board/{id}/claim   # 领取挑战任务
├── GET    /api/v1/my-challenges          # 我领取的挑战任务
├── POST   /api/v1/my-challenges/{id}/abandon   # 放弃挑战（可选惩罚）
├── POST   /api/v1/requests               # 发起申请（body 含 type: 'reward'|'task_proposal'）
├── GET    /api/v1/my-requests             # 我的申请列表（含两类历史）

任务审核 (Submissions) [含任务完成、任务提议、奖励申请三类审核]
├── GET    /api/v1/submissions            # 待审核打卡列表
├── GET    /api/v1/submissions/{id}       # 打卡详情
├── POST   /api/v1/submissions/{id}/approve   # 审核通过
├── POST   /api/v1/submissions/{id}/reject    # 驳回
├── POST   /api/v1/submissions/batch-approve  # 批量通过
├── GET    /api/v1/requests/pending            # 待审核孩子申请（含奖励申请+任务提议，可按type筛选）
├── POST   /api/v1/requests/{id}/approve       # 通过申请（奖励→直接发星 / 任务→生成挑战任务）
├── POST   /api/v1/requests/{id}/reject        # 驳回申请

奖励管理 (Rewards) [家长端]
├── GET    /api/v1/rewards                # 商店奖励列表
├── POST   /api/v1/rewards                # 创建商店奖励（名称/星星价格/图片）
├── PUT    /api/v1/rewards/{id}           # 编辑奖励
├── DELETE /api/v1/rewards/{id}           # 删除奖励
├── GET    /api/v1/rewards/{id}/history   # 兑换记录
├── GET    /api/v1/redemptions/pending    # 待审核兑换申请
├── POST   /api/v1/redemptions/{id}/approve  # 通过兑换（扣星）
└── POST   /api/v1/redemptions/{id}/reject   # 驳回兑换

星星与兑换 (Stars & Redemption) [孩子端]
├── GET    /api/v1/my-points              # 我的星星与流水
├── GET    /api/v1/rewards-shop           # 星星兑换商店（可兑换奖励列表）
├── POST   /api/v1/rewards/{id}/redeem    # 申请兑换奖励（提交审核）
└── GET    /api/v1/my-redemptions         # 我的兑换申请记录

数据统计 (Statistics)
├── GET    /api/v1/statistics/overview            # 家庭总览
├── GET    /api/v1/statistics/child/{id}          # 孩子维度统计（含必修/挑战分开的数据）
├── GET    /api/v1/statistics/child/{id}/trend    # 趋势数据
├── GET    /api/v1/statistics/tasks               # 任务维度统计（含挑战热度排行）
├── GET    /api/v1/statistics/report/weekly       # 周报
├── GET    /api/v1/statistics/report/monthly      # 月报
└── GET    /api/v1/statistics/export              # 数据导出

通知 (Notifications)
├── GET    /api/v1/notifications          # 通知列表
├── GET    /api/v1/notifications/unread-count  # 未读数
└── PATCH  /api/v1/notifications/{id}/read     # 标记已读

用户设置 (Profile)
├── GET    /api/v1/profile                # 个人信息
├── PUT    /api/v1/profile                # 更新个人信息
└── PUT    /api/v1/profile/password       # 修改密码
```

---

## 7. 前端页面结构

### 7.1 家长端页面

```
家长端 (Parent Portal)
│
├── /login                     登录页
├── /register                  注册页
│
├── /dashboard                 首页仪表盘
│   ├── 今日任务总览（按孩子分组）
│   ├── 待审核数量徽标
│   ├── 近 7 天完成率趋势小图
│   └── 快捷操作入口
│
├── /tasks                     任务管理中心
│   ├── 必修任务列表（筛选：状态/孩子/类型）
│   ├── 挑战任务列表（管理已发布的挑战）
│   ├── 创建任务弹窗（含必修/挑战切换开关）
│   ├── 任务模板快捷创建
│   ├── 挑战广场管理（上下架/调整倍率）
│   └── 批量操作
│
├── /review                    审核中心
│   ├── 待审核打卡列表
│   ├── 待审核孩子申请（奖励申请 + 任务提议，按类型标签区分）
│   ├── 审核详情（查看打卡照片/证据截图/备注）
│   ├── 通过/驳回（支持调整星星数 + 评语）
│   └── 审核记录历史
│
├── /rewards                   奖励管理
│   ├── 星星兑换商店管理（商品列表）
│   ├── 创建/编辑商店奖励
│   ├── 待审核兑换申请
│   └── 兑换记录查看
│
├── /statistics                数据统计
│   ├── 孩子选择器
│   ├── 完成率仪表盘
│   ├── 星星趋势折线图
│   ├── 任务完成分布（饼图/柱状图）
│   └── 周报/月报
│
├── /family                    家庭设置
│   ├── 家庭成员管理
│   ├── 星星规则配置
│   ├── 惩罚规则配置（家庭规则：连续未完成/完成率底线/挑战滥用防护）
│   ├── 徽章/成就配置
│   └── 邀请码管理
│
└── /profile                   个人设置
    ├── 个人信息编辑
    ├── 密码修改
    └── 通知偏好
```

### 7.2 孩子端页面

```
孩子端 (Child Portal)
│
├── /login                     登录页（支持简化登录）
│
├── /my-tasks                  我的必修任务
│   ├── 今日待完成（列表 + 进度条）
│   ├── 打卡提交（拍照 + 备注）
│   ├── 已完成列表
│   └── 任务日历视图
│
├── /challenge-board           挑战广场
│   ├── 可领取的挑战任务卡片列表
│   ├── 任务详情（星星倍率、时限、已领取人数）
│   └── 一键领取按钮
│
├── /my-challenges             我的挑战
│   ├── 进行中的挑战任务列表
│   ├── 打卡提交
│   └── 挑战完成记录
│
├── /submit-request            发起申请（统一入口）
│   ├── 顶部类型切换：「申请奖励」|「提议任务」
│   ├── 申请奖励表单：理由 + 证据截图 + 星星数
│   ├── 提议任务表单：名称 + 描述 + 分类 + 星星数 + 完成时间
│   └── 我的申请记录（含两类历史）
│
├── /my-points                 我的星星
│   ├── 当前星星余额
│   ├── 星星流水（区分获得/惩罚/兑换来源，惩罚项标红并显示原因）
│   └── 获得徽章展示
│
├── /reward-shop               星星兑换商店
│   ├── 奖励商品卡片网格（大图 + 名称 + 星价 + 库存）
│   ├── 每张卡片自带「兑换」按钮（一键提交审核）
│   └── 我的兑换申请记录（待审核/已兑现/已驳回）
│
├── /my-stats                  我的成绩
│   ├── 必修完成率统计
│   ├── 挑战参与与完成统计
│   ├── 连续打卡天数
│   └── 星星变化趋势
│
└── (可选) /family-board       家庭光荣榜
    └── 兄弟姐妹之间的友好对比（含挑战达人榜/星星富豪榜）
```

### 7.3 UI/UX 设计要求

- 家长端采用专业、高效的管理风格，以数据可视化为核心
- 孩子端采用活泼、友好的视觉风格（但不过于低幼），以任务清单和星星为核心
- 使用图标区分任务类型（书本=学习、扫帚=家务、牙刷=习惯、星星⭐=自定义）
- 使用视觉区分难度模式（盾牌🔒=必修、闪电⚡=挑战、奖杯🏆=挑战完成）
- 挑战广场采用卡片式布局，突出星星倍率数字，制造「抢任务」的紧迫感
- 星星兑换商店采用商品网格布局，大图+大号星价数字，刺激兑换欲望
- 关键操作不超过 3 步完成
- 支持 PWA，可在手机桌面添加快捷方式

---

## 8. Docker 容器化方案

### 8.1 服务拆分

```
┌──────────────────────────────────────────────────┐
│                  Docker Compose                    │
├────────────┬──────────┬─────────┬────────┬───────┤
│  nginx     │ backend  │ frontend│ redis  │  db   │
│  (反向代理) │ (FastAPI)│ (静态)  │ (缓存) │ (PG)  │
│  :80/:443  │  :8000   │         │ :6379  │ :5432 │
├────────────┴──────────┴─────────┴────────┴───────┤
│  celery-worker    │  celery-beat   │   minio     │
│  (异步任务)        │  (定时任务)     │  (文件存储)  │
│                   │                │   :9000     │
└───────────────────┴────────────────┴─────────────┘
```

### 8.2 docker-compose.yml 结构概览

```yaml
# 服务清单：
services:
  db:              # PostgreSQL 15
  redis:           # Redis 7
  minio:           # MinIO 对象存储
  backend:         # FastAPI 应用
  celery-worker:   # Celery 异步任务
  celery-beat:     # Celery 定时任务调度
  frontend:        # Nginx + Vue 静态文件
  nginx:           # 总入口反向代理

volumes:
  postgres_data:   # 数据库持久化
  redis_data:      # Redis 持久化
  minio_data:      # 文件存储持久化
```

### 8.4 Celery 异步任务清单

| 任务 | 触发方式 | 说明 |
|------|----------|------|
| `send_notification` | 事件驱动（API 调用后触发） | 创建站内通知记录，有 PWA 时同时推送 |
| `check_overdue_tasks` | 定时（每小时） | 扫描逾期未完成的必修任务，自动执行逾期打折 |
| `evaluate_penalty_rules` | 定时（每天凌晨） | 评估家庭惩罚规则（连续未完成/周完成率等），触发相应惩罚 |
| `generate_repeat_tasks` | 定时（每天凌晨） | 根据 repeat_type 自动生成次日的重复任务实例 |
| `check_streaks_and_badges` | 定时（每天凌晨） | 检查连续打卡天数，自动发放成就徽章和额外星星奖励 |
| `send_daily_reminder` | 定时（每天早8点，可配置） | 向孩子推送今日必修任务汇总 |
| `cleanup_old_notifications` | 定时（每周） | 归档 30 天前的已读通知 |
| `generate_weekly_report` | 定时（每周一） | 生成周报数据缓存，加速家长端统计页面加载 |

### 8.3 环境变量管理

通过 `.env` 文件统一管理所有服务的环境变量：

```bash
# 数据库
POSTGRES_DB=kids_star
POSTGRES_USER=kids_star
POSTGRES_PASSWORD=<secure_password>

# Redis
REDIS_PASSWORD=<secure_password>

# 应用
SECRET_KEY=<jwt_secret>
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=<secure_password>
MINIO_BUCKET=kids-star-uploads

# 邮件（通知用）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@kids-star.com
SMTP_PASSWORD=<email_password>
```

---

## 9. 安全设计

### 9.1 认证与授权

| 层面 | 措施 |
|------|------|
| 传输安全 | 全站 HTTPS，HSTS 头 |
| 密码存储 | bcrypt / argon2 哈希 |
| Token 管理 | JWT Access Token (短期) + Refresh Token (长期)，支持主动吊销 |
| 权限校验 | 每个 API 请求校验用户角色 + 家庭归属 |
| 孩子登录 | 简化登录（家庭邀请码 + 选择自己的头像/昵称），无需密码。首次由家长在家庭设置中为孩子创建账户并设定昵称和头像；孩子打开登录页 → 输入家庭邀请码 → 看到家庭成员列表 → 点选自己的头像 → 进入系统。此方式避免低龄孩子记忆密码的负担 |

### 9.2 数据安全

| 层面 | 措施 |
|------|------|
| 租户隔离 | 所有查询必须带 `family_id` 过滤，中间件强制注入 |
| SQL 注入 | ORM 参数化查询（SQLAlchemy） |
| XSS | 前端输出转义，CSP 头 |
| CSRF | SameSite Cookie + Token 头 |
| 文件上传 | 类型白名单、大小限制、病毒扫描（可选） |
| 速率限制 | 登录接口 5次/分钟，API 通用 100次/分钟（按用户） |

### 9.3 COPPA/GDPR 合规（未来扩展）

- 不收集儿童真实姓名，仅使用昵称
- 家长明确同意后才创建儿童账户
- 数据导出和账户删除功能
- 隐私政策页面

---

## 10. 开发路线图

### Phase 0 — 项目初始化 (v0.1.0)

> 搭建基础骨架，跑通 CI/CD

- [ ] 初始化前后端项目结构
- [ ] Docker Compose 开发环境
- [ ] 数据库迁移框架（Alembic）
- [ ] JWT 认证基础
- [ ] 前端路由框架 + 登录页 UI

### Phase 1 — 核心 MVP (v0.5.0)

> 最小可用产品，含必修+挑战双轨

- [ ] 用户注册/登录（家长 + 孩子简化登录）
- [ ] 家庭创建与成员管理
- [ ] 任务 CRUD（支持必修/挑战两种模式）
- [ ] 孩子端必修任务查看 + 打卡提交
- [ ] 挑战广场浏览 + 主动领取挑战
- [ ] 家长审核（通过/驳回）
- [ ] 基础星星加减（含挑战倍率）
- [ ] 任务内嵌惩罚（逾期打折/未完成扣星/挑战放弃冷却）
- [ ] 简单的今日任务仪表盘

### Phase 2 — 闭环完善 (v0.7.0)

> 核心流程闭环，体验完整

- [ ] 重复任务（每日/每周/每月，必修+挑战均支持）
- [ ] 任务模板库（含必修/挑战预设模板）
- [ ] 挑战任务领取限制与防占坑机制
- [ ] 家庭级惩罚规则配置（连续未完成/完成率底线/挑战滥用防护）
- [ ] 家长手动扣星功能
- [ ] 星星兑换商店（商品卡片内置兑换按钮 → 家长审核 → 扣星）
- [ ] 孩子统一发起申请（类型切换：奖励申请 / 任务提议）+ 家长审核分流处理
- [ ] 基础统计（必修完成率、挑战参与度、星星趋势）
- [ ] 通知系统（新必修任务、挑战上新、审核结果、申请状态）
- [ ] 拍照打卡上传
- [ ] 移动端适配优化

### Phase 3 — 增强特性 (v0.9.0)

> 差异化功能，体验提升

- [ ] 成就徽章系统（含挑战达人、全勤之星等专属徽章）
- [ ] 家庭光荣榜（含挑战星星排行）
- [ ] 周报/月报自动生成（必修+挑战分维度呈现）
- [ ] 数据导出（PDF/CSV）
- [ ] 挑战广场热度排序与个性化推荐
- [ ] PWA 支持
- [ ] 任务日历视图
- [ ] 批量操作优化

### Phase 4 — v1.0.0 正式发布

> 多家庭 SaaS 就绪，生产可用

- [ ] 性能优化与压力测试
- [ ] 安全审计
- [ ] 完整的 API 文档
- [ ] 部署文档与一键部署脚本
- [ ] 管理后台（平台运维）
- [ ] 错误监控（Sentry）
- [ ] 日志系统（ELK / Loki）

### Phase 5 — 未来规划 (v1.1.0+)

> 持续迭代方向

- [ ] 家校互通（老师角色）
- [ ] AI 任务建议（根据孩子表现推荐任务）
- [ ] 语音交互（低龄儿童友好）
- [ ] 国际化（i18n）
- [ ] 第三方登录（微信/Google）

---

## 11. 附录：术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 家庭 | Family | 数据隔离的核心单位，一个家庭包含多位家长和孩子 |
| 家长 | Parent | 家庭中的管理者角色 |
| 孩子 | Child | 家庭中的被管理者，任务的接收和执行者 |
| 任务 | Task | 家长创建并派发（或发布）给孩子的待完成事项 |
| 必修任务 | Required Task | 家长直接指派给孩子、必须完成的基础任务，星星 1x |
| 挑战任务 | Challenge Task | 家长发布到挑战广场、孩子自主领取的进阶任务，星星 1.5x~3x |
| 挑战广场 | Challenge Board | 孩子浏览和领取挑战任务的页面，展示当前所有可领取的挑战 |
| 领取 | Claim | 孩子主动接受挑战任务的动作 |
| 发起申请 | Submit Request | 孩子端统一入口，通过类型切换发起「奖励申请」或「任务提议」 |
| 奖励申请 | Reward Application | 孩子获得成就后主动发起的星星申请，需上传证据截图，由家长审核发放 |
| 任务提议 | Task Proposal | 孩子主动发起的自定义任务申请，家长审核通过后自动生成挑战任务并绑定到该孩子 |
| 打卡 | Check-in / Submit | 孩子完成任务后的提交动作 |
| 审核 | Review | 家长确认孩子任务完成/奖励申请/任务提议/兑换申请是否有效 |
| 星星 | Stars / Points | 系统的虚拟货币，完成任务/奖励申请获批获得，兑换奖励消耗（数据库字段保留 points） |
| 星星余额 | Star Balance | 孩子当前持有的星星数量，最低为 0（永不为负） |
| 惩罚 | Penalty | 因未完成/违规产生的星星扣除或功能限制，分三层：任务内嵌、家庭规则、手动惩罚 |
| 星星倍率 | Multiplier | 挑战任务相对于必修任务的星星倍数 |
| 星星兑换商店 | Star Shop | 孩子浏览奖励商品、发起兑换申请的页面，兑换需经家长审核 |
| 奖励 | Reward | 家长在商店中定义的可用星星兑换的虚拟或实物奖品 |
| 兑换 | Redemption | 孩子使用星星申请换取奖励的行为，需家长审核通过后扣星 |
| 补救任务 | Redemption Task | 家长可选开启的功能：孩子完成额外任务后抵消部分惩罚 |
| 徽章 | Badge | 达成特定条件后自动或手动授予的成就标记 |
| 租户 | Tenant | SaaS 概念，本系统中 Family = Tenant |

---

> **版本历史**  
> v1.0.0 (2026-05-30) — 初始完整规划设计，进入设计锁定阶段，待确认后启动 Phase 0 开发
