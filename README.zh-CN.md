<div align="center">

<img src="assets/banner.svg" alt="Gemini to Antigravity" width="100%"/>

# Gemini to Antigravity

**确定性的双 AI 接力协议：远端无限配额，本地构建权威。**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg?style=for-the-badge)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-8b5cf6.svg?style=for-the-badge)](SKILL.md)
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-4285F4.svg?style=for-the-badge)](https://docs.claude.com/en/docs/claude-code/skills)
[![No Telemetry](https://img.shields.io/badge/telemetry-none-0ea5e9.svg?style=for-the-badge)](#隐私与安全)

[English](README.md) · [简体中文](README.zh-CN.md) · [快速开始](#60-秒快速开始) · [技能规范](SKILL.md) · [协议](docs/PROTOCOL.md) · [安装](docs/AGENT-INTEGRATION.md)

</div>

<details>
<summary><b>目录</b></summary>

- [为什么要用](#为什么要用)
- [它解决的问题](#它解决的问题)
- [工作方式](#工作方式)
- [60 秒快速开始](#60-秒快速开始)
- [严谨性来自哪里](#严谨性来自哪里)
- [场景配方](#场景配方)
- [成本与延迟模型](#成本与延迟模型)
- [威胁模型](#威胁模型)
- [仓库结构](#仓库结构)
- [返回契约](#返回契约)
- [兼容性](#兼容性)
- [设计原则](#设计原则)
- [隐私与安全](#隐私与安全)
- [常见问题](#常见问题)
- [路线图](#路线图)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

</details>

---

## 为什么要用

每个认真写代码的智能体都会撞上同一堵墙：推理最强的模型有配额限制，配额无限（或极宽）的模型跑不了编译器。结果就是手工搬 diff、上下文丢失，最后才发现根本编译不过。

**Gemini to Antigravity** 把这种手工搬运固化成一套协议。

本地智能体 —— **A AI**（*Antigravity*：握有仓库、编译器和发布闸门）—— 负责诊断、审查与构建。远端智能体 —— **B AI**（*Gemini*：近乎无限的算力预算，零本地工具链）—— 负责批量代码改写。两端仅由两个产物连接：

```
一个交接 ZIP   ─────────────────────────▶   B AI
一个结果 ZIP   ◀─────────────────────────   B AI
```

其余一切 —— 不变量、提示词、返回契约、错误分级 —— 全部被编码，任何一端都不会漂移。

> 名字就是契约。*Gemini* 是你借来的引擎。*Antigravity* 是你永不离开的地面：你的仓库、你的 `git diff`、你的构建产物、你签下的发布。

---

## 它解决的问题

| 痛点 | 不用本技能 | 用本技能 |
| --- | --- | --- |
| **配额枯竭** | 把顶级模型配额烧在 400 行重构上 | 批量工作推给无限配额模型 |
| **远端无工具链** | 远端写出"看起来对"但永远编译不过的代码 | 本地侧必定编译、类型检查、打包 |
| **盲信** | 接受远端的"已完成"消息 | `git diff` 是事实来源，不是报告 |
| **上下文丢失** | 远端做到一半忘了架构 | `GEMINI_HANDOFF.md` 设计上自包含 |
| **接力乒乓** | 为一个漏掉的 import 来回三轮 | 机械性错误本地几秒修完 |
| **归档卫生** | `node_modules/` 把 ZIP 撑到 300 MB | 具名、可审计的排除清单 |
| **包装目录** | 文件多落一层，静默地什么都没覆盖 | 中转解压先归一化根目录 |
| **提交污染** | `GEMINI_HANDOFF.md` 被提交进仓库 | 交接产物显式不纳入版本控制 |

---

## 工作方式

<div align="center">
<img src="assets/flow.svg" alt="接力回路" width="100%"/>
</div>

```
┌────────────────────────── 阶段一 · 出站 ──────────────────────────┐
│  ① 预诊断    读源码、日志、堆栈                                   │
│              拆分「已确认问题」与「可疑区域」                      │
│  ② 交接提示  ZIP 根目录放 GEMINI_HANDOFF.md                       │
│              → 任务、约束、返回契约                                │
│  ③ 打包      ZIP_DEFLATED，compresslevel = 9                      │
│              排除 .git、node_modules、build、dist …               │
└───────────────────────────────────────┬───────────────────────────┘
                                        ▼
                              ┌─────────────────┐
                              │  B AI / ZIP     │  批量改写，无构建
                              └────────┬────────┘
                                       ▼
┌────────────────────────── 阶段二 · 入站 ──────────────────────────┐
│  ④ 安全点    git status → commit / 具名 stash                     │
│  ⑤ 中转解压  检查目录布局 → 归一化包装层                           │
│              完整读取 CHANGE_REPORT.md                            │
│              覆盖源码，按「Deleted Files」删除                      │
│  ⑥ Diff 审查 git status · git diff --stat · git diff              │
│              对照报告与原始需求双重复核                           │
│  ⑦ 构建闸门  typecheck → 编译 → 测试 → 发布产物                   │
│  ⑧ 分级处理  机械性 → 本地修复重编                                │
│              结构性 → 驳回，重做 ZIP                              │
└───────────────────────────────────────────────────────────────────┘
```

---

## 60 秒快速开始

### 安装

```bash
# 个人级技能（所有项目可用）
git clone https://github.com/HIMKUG/gemini-to-antigravity.git \
  ~/.claude/skills/gemini-to-antigravity
```

```powershell
# Windows PowerShell
git clone https://github.com/HIMKUG/gemini-to-antigravity.git "$env:USERPROFILE\.claude\skills\gemini-to-antigravity"
```

也可以把目录放进单个项目的 `.claude/skills/` 下做项目级作用域。

验证加载：

```bash
claude --debug 2>&1 | grep -i gemini-to-antigravity
```

### 出站用法

> "把这个仓库打包给 Gemini。崩溃点在 `src/core/scheduler.ts:112`，把修复交接过去，并让它顺带审计重试路径。"

实际发生：预诊断 → 生成 `GEMINI_HANDOFF.md` → 最大压缩生成 `repo-handoff-<日期>.zip` → 输出精确路径与字节数供你上传。

### 入站用法

> "这是 Gemini 返回的 ZIP。应用它、审查 diff，然后构建 release APK。"

实际发生：安全点 → 中转解压 → 覆盖 → `git diff` 审查 → 构建 → 本地分级修复 → 报告发布产物路径。

---

## 严谨性来自哪里

### 1 · 交接提示按契约自包含

B AI 不认识本技能、这个仓库或之前的对话。它必须遵守的每条不变量全部写在 `GEMINI_HANDOFF.md` 里：

| 章节 | 保证 |
| --- | --- |
| **环境说明** | 告知 B AI 没有编译器，必须静态推理 import、类型与符号 |
| **用户原始需求（逐字）** | 不允许改写漂移，需求逐字节穿越运输 |
| **已确认问题** | 文件路径 + 行号 + 根因，交接前已在本地验证 |
| **可疑区域** | 点名 B AI 必须审计的盲区，区分「已知坏」与「可能坏」 |
| **交付与返回契约** | 精确的 ZIP 形状、精确的 `CHANGE_REPORT.md` 结构、显式删除清单 |

### 2 · 归档是规格，不是倾倒

| 包含 | 排除（黑名单） |
| --- | --- |
| 完整源码树、全部配置、锁文件、资源 | `.git/` |
| 根目录 `GEMINI_HANDOFF.md` | `node_modules/`、`.venv/`、`__pycache__/` |
| 与 `.gitignore` 相关的源码文件 | `target/`、`build/`、`dist/`、`.gradle/`、`.dart_tool/` |
| 逐字节保留的相对目录结构 | `.idea/`、`.vs/`、`.DS_Store` |

压缩：`zipfile.ZIP_DEFLATED` + `compresslevel=9`（跨平台、无需外部二进制），或可用的 `zip -9 -r`。写完即校验：根目录存在 `GEMINI_HANDOFF.md`、相对布局完整保留。

### 3 · 集成是双钥匙操作

你永远不会把远端归档直接解到工作树。两道闸门：

1. **安全点** —— 先 `git status`；提交或建具名 stash，覆盖前状态永远可恢复。
2. **中转解压** —— 解到临时目录，识别包装层（`project_name/`），归一化源码根，**先读完报告再复制任何文件**。

### 4 · Git 是裁判

远端报告只是*主张*，`git diff` 才是*证据*。审查是强制且结构化的：

- `git status`、`git diff --stat` 看清影响面
- 完整 `git diff` 判断意图
- 同时对照 `CHANGE_REPORT.md` **与**逐字原始需求
- 主动排查截断、格式噪声、越界改动

### 5 · 错误分级是决策，不是条件反射

| 类别 | 例子 | 动作 |
| --- | --- | --- |
| **机械性** | 缺 import、漏依赖声明、语法笔误、可见性不匹配 | 本地修复、重编、发布 |
| **结构性** | 漏掉核心需求、架构缺陷、diff 审查失败 | 停止打补丁；带日志与 diff 片段重写交接；重发 |

本地补一个 import 只要几秒，远端一次人肉接力要一整个来回。协议禁止把它打回去。

---

## 场景配方

针对本协议存在的四类情境，可直接复制的提示词。

### 配方 A · 修复间歇性崩溃

```text
出站："打包给 Gemini。崩溃在 src/core/scheduler.ts:112。
已确认：缺少 paused 状态守卫。可疑：queue 出队路径。
修复并审计可疑区域，返回 ZIP + CHANGE_REPORT.md。"
入站："应用 ZIP、审查 diff、类型检查、跑 scheduler 测试、构建。"
```
生效的分级规则：构建中暴露的缺失 import 在本地补，绝不打回。

### 配方 B · 无限配额上做全新功能

```text
出站："交接设置页功能。已确认：src/app/settings 下无既有路由。
可疑：导航注册表、主题 token。交付完整树，不得删除任何文件。"
入站："中转解压、审查 diff、排查越界改动，然后构建并冒烟测试。"
```
`Deleted Files` 是绊线 —— 全新功能应报告 `None`。

### 配方 C · 机械性横扫（改名、格式化、依赖升级）

```text
出站："全仓库把 TaskHandler 改名为 JobHandler。行为不变。
返回完整树；从未提及 TaskHandler 的文件可跳过。"
入站："应用后用 git diff --stat 核对影响面，与本地 grep 计数一致。"
```
横扫最适合激进审查 diff：任何符号引用之外的改动都是漂移。

### 配方 D · 移植或迁移

```text
出站："把 src/legacy/export.ts 从 CommonJS 移植到 ESM。
已确认：6 处调用点（行号见下）。可疑：动态 require、barrel 文件。"
入站："应用、逐处审查 import 重写，然后跑完整包构建。"
```
移植失败常因*遗漏*，所以 `Build & Dependency Notes` 要优先读。

---

## 成本与延迟模型

为什么"双产物"设计优于随手复制粘贴：

| 因素 | 聊天式复制粘贴 | 本协议 |
| --- | --- | --- |
| 前沿模型 token | 高 —— 每轮重新解释仓库 | 低 —— 只看到审查过的 diff |
| 远端模型 token | 按粘贴计费，格式有损 | 一个 `-9` 归档，结构完整 |
| 机械性错误往返 | 2–3 次 | 0 次 —— 本地修复 |
| 结构性错误往返 | 2 次以上且上下文丢失 | 1 次，附带日志与 diff 片段 |
| 每轮人工注意力 | 重粘、重讲、重信任 | 审 diff，批准或驳回 |
| 可复现性 | 无 —— 每次粘贴都不同 | 归档 + 逐字需求 = 可审计 |

归档是工作单元，其余都是对该单元的审查步骤。

---

## 威胁模型

本协议防御什么，以及不防御什么。

| 威胁 | 缓解 | 残余风险 |
| --- | --- | --- |
| 密钥泄入交接包 | `.env*`、`*.pem`、`*.key` 黑名单，打包器写后扫描 | 以异常文件名伪装的密钥 |
| 破坏性覆盖 | 写前 Git 安全点；中转解压 | 从未 stash 的本地未提交改动 |
| 静默删文件 | `Deleted Files` 是唯一授权删除通道 | 报告写 `None` 却实际删除 —— 由 `git status` 捕获 |
| 越界改动 | 完整 `git diff` 对照逐字需求 | 超大 diff 的审查疲劳 —— 拆分交接 |
| 远端代码不可构建 | 本地强制构建闸门 | 能构建但行为错误 —— 由测试兜底 |
| 供应链注入 | `Build & Dependency Notes` 在进入构建前点名新依赖 | 加了依赖却没报告 —— 由锁文件 diff 捕获 |
| 归档炸弹 / 超大 ZIP | 排除清单 + 字节数报告 | 确实应进归档的二进制资源 |

不防御：恶意远端模型在请求范围内植入后门逻辑。diff 审查与测试是你唯一的控制手段 —— 读 diff，不要读报告。

---

## 仓库结构

```
gemini-to-antigravity/
├── SKILL.md                      # 技能本体：面向智能体的规范
├── README.md                     # 英文说明
├── README.zh-CN.md               # 简体中文说明（本文件）
├── LICENSE                       # MIT
├── assets/
│   ├── banner.svg                # README 头图
│   └── flow.svg                  # 接力示意图
├── examples/
│   ├── GEMINI_HANDOFF.example.md # 出站提示示例
│   └── CHANGE_REPORT.example.md  # 入站报告示例
├── scripts/
│   └── pack_handoff.py           # ZIP -9 打包 + 写后校验
├── docs/
│   ├── PROTOCOL.md               # 形式化不变量、状态机、一致性清单
│   ├── AGENT-INTEGRATION.md      # 安装到 Claude Code、Cursor、Codex、MCP
│   ├── COMPARISON.md             # 与复制粘贴、补丁接力、分支交接对比
│   └── OPERATIONS.md             # 轮次规模、调度、升级处置手册
└── .github/workflows/validate.yml # CI：schema、打包器冒烟、链接检查
```

| 文档 | 何时读 |
| --- | --- |
| [SKILL.md](SKILL.md) | 你是执行一轮接力的智能体 |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | 需要形式化不变量或一致性清单 |
| [docs/AGENT-INTEGRATION.md](docs/AGENT-INTEGRATION.md) | 正在把本技能装进某个运行时 |
| [docs/COMPARISON.md](docs/COMPARISON.md) | 正在判断本协议是否适用 |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | 某轮失败，或准备连做多轮 |
| [examples/](examples) | 想要可直接照抄的交接与报告 |
| [CHANGELOG.md](CHANGELOG.md) | 想知道改了什么、为什么改 |

---

## 返回契约

B AI 必须只回一个 ZIP：

```text
<result>.zip
├── <源码树，相对布局不变>
└── CHANGE_REPORT.md
```

`CHANGE_REPORT.md` 结构：

```markdown
## Summary of Changes
- path/to/file.ext — <改了什么、为什么>

## Findings on Suspect Areas
- path/module — <检查了什么、发现了什么、修了什么>

## Deleted Files
- path/to/removed.ext        # 或字面值：None

## Build & Dependency Notes
- 需要在本地验证的新依赖、权限、import 或构建步骤
```

缺失四节中任何一节，即视为未完成交付。

---

## 兼容性

| 环境 | 支持 |
| --- | --- |
| Claude Code（CLI / 桌面 / IDE） | ✅ 自动从 `~/.claude/skills` 发现 |
| 任何读取 `SKILL.md` 的智能体运行时 | ✅ 纯 Markdown + YAML frontmatter |
| 仓库语言 | ✅ 语言无关：TS、Python、Rust、Kotlin、Dart、C++ 等 |
| 发布目标 | ✅ 二进制、安装包、APK、Bundle、容器 |
| 操作系统 | ✅ Windows、macOS、Linux |
| 网络 | ❌ 不需要 —— 接力设计上基于文件 |

---

## 设计原则

1. **本地权威不可让渡。** 持有编译器的一方永远拥有最终解释权。
2. **产物优先于承诺。** ZIP 与 diff 高于任何"已完成"的散文。
3. **规则随载荷同行。** 自包含提示优于隐含上下文。
4. **便宜修复保持便宜。** 机械性错误不配一次接力来回。
5. **最小干净归档。** 被排除的字节即被排除的风险。
6. **默认可逆。** 每次覆盖前必有安全点。
7. **无隐藏状态。** 整套协议就是本仓库里可读的 Markdown。

---

## 隐私与安全

- **无遥测。** 技能不发起网络请求，不向任何地方上报。
- **无凭据。** 交接产物只含源码，绝不含 `.env`、令牌或密钥。敏感仓库请自行把密钥模式加入排除清单。
- **人在回路。** ZIP 由你自己上传，不存在自动外发。
- **交接文件不入库。** `GEMINI_HANDOFF.md` 与 `CHANGE_REPORT.md` 不进入提交，仓库历史保持干净。

---

## 常见问题

**为什么不直接用配额更大的单一模型？**
因为配额与工具链极少同处一地。本协议让你组合两者优势而不丢发布闸门。

**A AI 可以是别的本地智能体吗？**
可以。任何能读写文件、跑 `git`、执行构建的都合格，`SKILL.md` 与模型无关。

**B AI 必须用 Gemini 吗？**
不必 —— 任何能接收 ZIP 并返回 ZIP 的远端模型都行，契约就是接口。

**交接包能多大？**
由排除后的源码决定，通常几 MB。二进制资源是实际上限，超大媒体建议改用清单引用。

**B AI 返回带包装目录怎么办？**
这是预期情况，中转解压会归一化。它是远端 ZIP 最常见的失败模式，已被显式处理。

**B AI 删了我需要的文件？**
`Deleted Files` 是唯一授权的删除通道。未出现在该节的删除属于协议违规，会在 diff 审查中暴露。

**支持 monorepo 吗？**
支持。排除清单按相对路径生效，布局逐字保留，工作区结构完好。

**有自动打包器吗？**
有 —— [`scripts/pack_handoff.py`](scripts/pack_handoff.py) 用默认黑名单产出 `-9` 归档，并校验交接文件位于根目录、未混入任何密钥文件。

---

## 路线图

- [ ] 返回 ZIP 的 `--verify` 审计模式（布局、报告结构、删除项）
- [ ] 可配置黑名单档案（`web`、`android`、`python`、`monorepo`）
- [ ] 覆盖前的交接 diff 预览
- [ ] 多轮接力历史与逐轮检查点
- [ ] `GEMINI_HANDOFF.md` 完整性预检 lint

见 [Issues](https://github.com/HIMKUG/gemini-to-antigravity/issues)，欢迎提案。

---

## 参与贡献

先读 [CONTRIBUTING.md](CONTRIBUTING.md)，然后提 PR。保持 `SKILL.md` 与模型无关、协议可读、diff 精简。

```bash
git clone https://github.com/HIMKUG/gemini-to-antigravity.git
cd gemini-to-antigravity
git checkout -b feat/your-change
```

---

## 许可证

MIT © 2026 HIMKUG —— 见 [LICENSE](LICENSE)。

<div align="center">

**借来引擎，守住地面。**

<sub>为真正交付的智能体而建，不为聊天的智能体而建。</sub>

</div>
