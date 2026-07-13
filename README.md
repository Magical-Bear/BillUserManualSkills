# Doctor Bill Skill v2

> Doctor Bill 是用户级研发协作 Skill。执行身份：`super_bill`。

Doctor Bill 覆盖需求分析、软件、硬件、AI、运维、开发、测试、验收和部署流程。它不是单个提示词，而是一套可安装到 Codex、Claude Code 和 Cursor 用户环境的 Skill/规则入口。

## 核心原则

- 严格遵循用户指令。
- 没有清楚到小白能看懂的需求/架构文档，并且用户未批准前，禁止开发。
- 开发 Agent 只开发。
- 测试 Agent 只测试，不修改生产代码。
- 用户验收并明确同意后，才允许合并 `main` 或 push。
- 最终报告必须说明风险改动、判断依据、时间窗口、超时、重试、阈值和变量位置。

## Skill 结构

```text
.
├── SKILL.md                         # doctor-bill 主入口
├── persona.md                       # 保留原有人设
├── work.md                          # 旧版知识兼容导航
├── agents/
│   ├── openai.yaml
│   ├── developer.md                 # 开发 Agent
│   └── tester.md                    # 测试 Agent
├── references/
│   ├── skill-routing.md
│   └── legacy-work-knowledge.md
├── skills/
│   ├── doctor-bill-software/
│   ├── doctor-bill-hardware/
│   ├── doctor-bill-ai/
│   └── doctor-bill-ops/
├── adapters/
│   ├── codex/AGENTS.md
│   ├── claude/CLAUDE.md
│   └── cursor/doctor-bill.mdc
└── scripts/
    ├── install.sh
    ├── uninstall.sh
    ├── validate-skills.py
    └── validate-install.py
```

## 五个 Skill

| Skill | 作用 |
|---|---|
| `doctor-bill` | 主入口、工具门禁、需求批准、领域路由、角色隔离、分支/合并门禁 |
| `doctor-bill-software` | 产品、前后端、API、数据库、UI、ECharts、异步软件架构 |
| `doctor-bill-hardware` | ESP32、STM32、传感器、串口、MQTT、固件和设备数据链路 |
| `doctor-bill-ai` | Dify、LangChain、RAG、Agent、微调、vLLM、ASR/TTS、多模态和评估 |
| `doctor-bill-ops` | Linux、systemd、linger、无 sudo、GitHub Actions SSH 部署、健康检查和回滚 |

## 强制工具门禁

Doctor Bill 的正式研发流程要求：

1. 需求讨论必须使用 `superpowers`。
2. 技术选型和架构分析必须使用 `Context7` 查询当前版本官方文档。
3. 涉及 UI、管理后台、报表、大屏、ECharts、布局或视觉设计时，必须使用 `ui-ux-pro-max-skill`。

缺失时停止对应阶段，引导用户安装并验证后继续。

## 默认软件架构

用户和现有项目没有指定其他方案时：

- Python 3.11+ 和 uv。
- FastAPI + Pydantic v2。
- SQLAlchemy 2.x ORM。
- async engine + `async_sessionmaker`。
- engine/session factory 放在 lifespan 管理。
- 请求级 `AsyncSession`，禁止全局共享 session。
- 优先服务器已有 MySQL。
- Redis 异步客户端。
- aiohttp 对外 HTTP 请求。
- Python 3.11+ `asyncio.TaskGroup`。
- APScheduler 异步定时任务。
- Vue 3 + Vite。
- ECharts。

数据库默认第三范式。报表允许聚合表或受控冗余，但必须保留原始数据，聚合结果可重算，协议字段向后兼容。

## 运维默认规则

- 有 sudo 且用户批准时可以设计 system service。
- 无 sudo 时优先 systemd user service：`~/.config/systemd/user/` + `systemctl --user`。
- 必须检查 linger：`loginctl show-user <user> -p Linger`。
- 当前用户无法启用 linger 时，给管理员命令，不绕权限。
- GitHub Actions 部署使用 main push + SSH + known_hosts + Secrets + concurrency 锁。
- 部署步骤包含项目目录、`uv sync`、已批准迁移、服务重启、健康检查、日志采集和回滚。
- 自动重启不等于零停机；零停机需要单独设计蓝绿/滚动/切流。

## 安装

### Codex

```bash
./scripts/install.sh --platform codex
```

默认安装到：

```text
~/.codex/skills/doctor-bill
~/.codex/skills/doctor-bill-software
~/.codex/skills/doctor-bill-hardware
~/.codex/skills/doctor-bill-ai
~/.codex/skills/doctor-bill-ops
~/.codex/AGENTS.md
```

覆盖路径：

```bash
./scripts/install.sh --platform codex --codex-home /path/to/.codex
```

### Claude Code

```bash
./scripts/install.sh --platform claude
```

默认安装到：

```text
~/.claude/skills/doctor-bill
~/.claude/skills/doctor-bill-software
~/.claude/skills/doctor-bill-hardware
~/.claude/skills/doctor-bill-ai
~/.claude/skills/doctor-bill-ops
~/.claude/CLAUDE.md
```

覆盖路径：

```bash
./scripts/install.sh --platform claude --claude-home /path/to/.claude
```

### Cursor

Cursor 的用户级 Rules 路径会随版本、平台和用户配置变化。不要盲猜。

验证策略：

1. 打开 Cursor 设置，查找 Rules/User Rules/Project Rules 的实际存放目录。
2. 或确认当前机器是否存在 `~/.cursor/rules`。
3. 将确认后的目录传给安装器。

```bash
./scripts/install.sh --platform cursor --cursor-rules-dir /verified/cursor/rules/path
```

如果本机存在 `~/.cursor/rules` 且没有传参，安装器会使用它；否则会跳过 Cursor 并提示传参。

### 全部平台

```bash
./scripts/install.sh --platform all
```

### dry-run

```bash
./scripts/install.sh --platform all --dry-run
```

安装器会：

- 安全备份已存在 Skill 目录。
- 通过 `<!-- DOCTOR-BILL:BEGIN -->` / `<!-- DOCTOR-BILL:END -->` 标记区块更新入口文件。
- 不写入密钥。

## 卸载

```bash
./scripts/uninstall.sh --platform all
```

卸载器会把安装目录移动到带时间戳的备份，并从入口文件移除 Doctor Bill 标记区块。

## 校验

源码结构校验：

```bash
python3 scripts/validate-skills.py
```

安装产物校验：

```bash
python3 scripts/validate-install.py --platform codex
python3 scripts/validate-install.py --platform claude
python3 scripts/validate-install.py --platform cursor --cursor-rules-dir /verified/cursor/rules/path
```

临时目录完整验证示例：

```bash
TMP_ROOT=/tmp/doctor-bill-install-check
./scripts/install.sh \
  --platform all \
  --codex-home "$TMP_ROOT/codex" \
  --claude-home "$TMP_ROOT/claude" \
  --cursor-rules-dir "$TMP_ROOT/cursor-rules"
python3 scripts/validate-install.py \
  --platform all \
  --codex-home "$TMP_ROOT/codex" \
  --claude-home "$TMP_ROOT/claude" \
  --cursor-rules-dir "$TMP_ROOT/cursor-rules"
```

## 开发/测试/验收流程

```text
需求讨论(superpowers)
  → 架构分析(Context7)
  → UI 方案(ui-ux-pro-max-skill，如涉及 UI)
  → 用户批准
  → 非 main 分支开发
  → 开发 Agent 报告风险和变量位置
  → 测试 Agent 静态→单元→集成→E2E→冒烟
  → 用户验收
  → 用户明确同意后合并 main/push
```

API E2E 测试必须使用 `asyncio + httpx.AsyncClient` 请求真实运行服务，禁止 mock。

## 安全说明

- 不读取生产 `.env`，除非用户明确允许。
- 不提交密码、Token、私钥和生产环境文件。
- 不擅自执行破坏性 Git 操作。
- 不同时充当守门员和裁判员。

## License

MIT
