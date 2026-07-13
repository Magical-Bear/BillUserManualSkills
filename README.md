# Doctor Bill Skills

> 执行身份：`super_bill`。公开人物与 Skill 品牌：贝尔 / Doctor Bill。

Doctor Bill 是一套用户级工程协作 Skills，覆盖需求讨论、软件、硬件、AI、运维、开发 Agent、测试 Agent、Git、验收和部署。

## 架构

只保留一个主 Skill 和四个领域 Skill。所有强制规则都直接写在对应 `SKILL.md`，不使用 `references`、`work.md` 或独立开发/测试说明文件承载关键行为。

```text
.
├── SKILL.md                         # 主 Skill：身份、门禁、路由、Agent、Git、验收
├── persona.md                       # 原始完整人设归档；主 Skill 已内置必需身份规则
├── agents/openai.yaml               # 主 Skill UI 元数据
├── skills/
│   ├── doctor-bill-software/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── doctor-bill-hardware/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── doctor-bill-ai/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   └── doctor-bill-ops/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── assets/
│           ├── systemd/*.service
│           ├── github/deploy-main.yml
│           └── deploy/deploy.sh
├── adapters/
│   ├── codex/AGENTS.md
│   ├── claude/CLAUDE.md
│   └── cursor/doctor-bill.mdc
├── tests/behavior-scenarios.json
└── scripts/
    ├── install.sh
    ├── uninstall.sh
    ├── validate-skills.py
    ├── validate-install.py
    └── test-behavior-contract.py
```

`assets` 只包含可以直接复制和参数化的 systemd、GitHub Actions 和部署模板，不承载隐藏规则。

## 五个 Skill

| Skill | 职责 |
|---|---|
| `doctor-bill` | 身份、工具门禁、场景需求、领域路由、开发/测试隔离、Git、验收和报告 |
| `doctor-bill-software` | 软件、异步 API、SQLAlchemy 数据库、报表、UI、可观测性和软件测试 |
| `doctor-bill-hardware` | ESP32、STM32、传感器、协议、MQTT、离线补传和设备链路 |
| `doctor-bill-ai` | Dify、RAG、Agent、FastMCP、模型、推理、微调、评估和 AI 数据治理 |
| `doctor-bill-ops` | systemd、linger、无 sudo 服务、Actions 自动部署、健康检查和回滚 |

四个领域 Skill 禁止隐式调用。它们的 `default_prompt` 要求先使用 `$doctor-bill`，避免绕过主门禁。

## 核心门禁

1. 正式需求讨论必须使用 `superpowers`。
2. 架构和技术选型必须使用 `Context7` 查询当前官方文档。
3. 涉及 UI、报表、ECharts、后台、大屏、布局或视觉时必须使用 `ui-ux-pro-max-skill`。
4. 缺失能力时停止对应阶段，引导安装和验证。
5. 没有小白可读的需求/架构文档且用户未批准前禁止开发。
6. 正式开发必须在非 `main` 分支。
7. 开发 Agent 完成后才能派测试 Agent；测试 Agent 不修改被测生产代码。
8. 用户验收并明确同意后才能合并或 push main。

决策优先级：

```text
用户明确要求
> 现有项目约束
> 当前官方兼容性和安全要求
> super_bill 默认技术偏好
```

FastAPI、aiohttp、APScheduler、Vue、ECharts、vLLM 等属于默认偏好，不是所有项目的绝对要求。

## 数据库规则

除非用户明确指定其他方案架构：

- 必须 SQLAlchemy 2.x ORM。
- 必须 async engine、`async_sessionmaker`、`AsyncSession`。
- engine/session factory 由 lifespan 创建和释放。
- session 请求级或任务级隔离，禁止全局共享。
- 优先服务器现有 MySQL。
- 开发数据库与测试数据库必须分离。
- 业务主数据默认第三范式。
- 报表可使用聚合表，但必须保留原始数据、版本化、可重算并向后兼容。

软件 Skill 包含“每 3 分钟上报、每小时理论 20 个样本”的完整示例，要求确认聚合公式、缺失、去重、迟到、时区和重算。

## 安装

安装器会备份已存在的同名 Skill/入口，并安装完整五个 Skill。

### Codex

```bash
./scripts/install.sh --platform codex
```

默认目标：

```text
~/.codex/skills/doctor-bill*
~/.codex/AGENTS.md
```

### Claude Code

```bash
./scripts/install.sh --platform claude
```

默认目标：

```text
~/.claude/skills/doctor-bill*
~/.claude/CLAUDE.md
```

### Cursor

```bash
./scripts/install.sh --platform cursor
```

默认目标：

```text
~/.cursor/skills/doctor-bill*
~/.cursor/rules/doctor-bill.mdc
```

Cursor 不同版本或配置的用户级 Rules/Skills 目录可能不同。安装前先确认当前配置；不同时显式覆盖：

```bash
./scripts/install.sh --platform cursor \
  --cursor-rules-dir /verified/user/rules \
  --cursor-skills-dir /verified/user/skills
```

### 全平台或自定义用户目录

```bash
./scripts/install.sh --platform all
./scripts/install.sh --platform all --dry-run
./scripts/install.sh --platform codex --codex-home /path/to/.codex
./scripts/install.sh --platform claude --claude-home /path/to/.claude
```

安装完成后重新启动或重新加载对应 Agent，并确认能识别 `doctor-bill`、四个领域 Skill 和用户级入口。

## 缺失依赖的处理

Doctor Bill 不伪造第三方 Skill/MCP 安装命令。先按当前平台检查：

- `superpowers` 是否出现在可用 Skills 中。
- `Context7` 是否出现在可用 MCP/工具中。
- `ui-ux-pro-max-skill` 是否出现在可用 Skills 中。

缺失时使用平台当前支持的用户级 Skill 安装器或 MCP 配置安装，重新加载平台并验证名称可见；验证前不进入对应正式阶段。

## 运维模板

`doctor-bill-ops/assets` 提供：

- systemd system service 模板。
- systemd user service 模板。
- main push GitHub Actions workflow。
- 检查脏工作树、`pull --ff-only`、依赖同步、可选迁移、重启、健康检查、日志和回滚的部署脚本。

使用前必须替换占位符和变量，并在测试环境验证。自动更新并重启不等于严格零停机。

## 校验

```bash
bash -n scripts/install.sh scripts/uninstall.sh skills/doctor-bill-ops/assets/deploy/deploy.sh
python3 scripts/validate-skills.py
python3 scripts/test-behavior-contract.py
```

临时目录安装验证：

```bash
TMP_ROOT="$(mktemp -d)"
./scripts/install.sh --platform all \
  --codex-home "$TMP_ROOT/codex" \
  --claude-home "$TMP_ROOT/claude" \
  --cursor-home "$TMP_ROOT/cursor"
python3 scripts/validate-install.py --platform all \
  --codex-home "$TMP_ROOT/codex" \
  --claude-home "$TMP_ROOT/claude" \
  --cursor-home "$TMP_ROOT/cursor"
```

`validate-skills.py` 验证五 Skill 自包含结构和确认需求矩阵；`test-behavior-contract.py` 验证六个典型场景的规则覆盖。它们不冒充独立模型行为测试，发布前仍需测试 Agent 做真实前向检查。

## 卸载

```bash
./scripts/uninstall.sh --platform all
```

卸载时不会直接删除安装产物，而是移动到带时间戳的备份，并从 `AGENTS.md`/`CLAUDE.md` 移除 Doctor Bill 标记区块。

## License

MIT
