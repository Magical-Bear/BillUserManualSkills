---
name: doctor-bill-ops
description: Doctor Bill 运维领域 Skill。用于 Linux、systemd system/user service、无 sudo linger、GitHub Actions SSH 自动部署、main 更新重启、健康检查、日志和回滚；必须由 doctor-bill 主 Skill 编排。
---

# Doctor Bill Ops

## 1. 调用边界

- 执行身份是 `super_bill`，品牌是贝尔 / Doctor Bill。
- 本 Skill 不能绕过主 Skill 的需求批准、风险确认、分支、独立测试和用户验收。
- 生产部署、权限提升、迁移、重启、回滚和修改用户级系统文件前必须说明影响并得到授权。

## 2. 运维前检查

先检查并记录：

- OS、发行版、架构、用户、shell、时区和时间同步。
- sudo 权限、systemd 版本、user manager 和 linger。
- 项目目录、所有者、磁盘、端口、防火墙和反向代理。
- Git 分支、remote、工作树、部署用户和 SSH 配置。
- Python/uv/Node/Docker、数据库、Redis 和外部依赖。
- 如环境提供经批准的 SSH MCP，可用于连接服务器，但仍遵守主机校验、最小权限和生产授权。
- 当前服务、日志、健康接口、备份和回滚能力。

禁止：

- 未授权读取生产 `.env`、私钥和 secrets。
- 默认关闭 SSH host key、TLS 或防火墙验证。
- 覆盖服务器脏工作树。
- 将数据库迁移默认等同于安全操作。

## 3. systemd 选择

### 有 sudo

可安装 system service：

```text
/etc/systemd/system/<service>.service
sudo systemctl daemon-reload
sudo systemctl enable --now <service>.service
```

### 无 sudo

优先 user service：

```text
~/.config/systemd/user/<service>.service
systemctl --user daemon-reload
systemctl --user enable --now <service>.service
```

必须检查 user manager 和 linger：

```bash
loginctl show-user "$USER" -p Linger
systemctl --user status
```

如果退出登录后仍需运行，需要 linger。当前用户不能自行启用时，明确告诉用户由管理员执行：

```bash
sudo loginctl enable-linger <user>
```

禁止绕过权限或谎称 linger 已开启。

## 4. systemd 单元要求

模板见本 Skill 的 `assets/systemd/`，使用前必须替换占位符并按项目验证。

至少配置和说明：

- `Description`
- `After` / `Wants`
- `User`/`Group`（system service）
- `WorkingDirectory`
- `EnvironmentFile`
- `ExecStart`
- `ExecReload`（确有支持时）
- `Restart`
- `RestartSec`
- `TimeoutStartSec`
- `TimeoutStopSec`
- `KillSignal`
- `StartLimitIntervalSec`
- `StartLimitBurst`
- `WantedBy`

规则：

- `ExecStart` 使用绝对路径。
- EnvironmentFile 权限最小化，不把 secrets 写进 unit。
- user service 使用 `WantedBy=default.target`；system service 通常使用 `multi-user.target`。
- restart 阈值按应用启动时间和故障模式配置，不能无限快速重启。
- 服务必须正确处理 SIGTERM、停止接收、等待任务和关闭资源。

## 5. 启停、日志和健康检查

部署后至少执行：

```bash
systemctl [--user] status <service> --no-pager
journalctl [--user] -u <service> -n 200 --no-pager
curl --fail --show-error --max-time <seconds> <health-url>
```

健康检查区分：

- liveness：进程是否存活。
- readiness：数据库、Redis、关键依赖是否达到接流条件。

记录启动时间、健康超时、重试次数、重试间隔和判定阈值。

## 6. GitHub Actions 自动部署前置条件

先引导用户配置：

- 专用、最小权限部署用户。
- 专用 SSH Key，不复用个人主密钥。
- 公钥写入服务器部署用户 `authorized_keys`。
- 私钥写入 GitHub Actions secret。
- 已验证的 SSH `known_hosts` 内容，禁止默认 `StrictHostKeyChecking=no`。
- 部署主机、端口、用户、项目目录、服务模式、服务名和健康接口。
- 服务器仓库访问凭据。
- 是否允许数据库迁移及迁移命令。

建议变量：

```text
DEPLOY_HOST
DEPLOY_PORT
DEPLOY_USER
DEPLOY_SSH_KEY
DEPLOY_KNOWN_HOSTS
APP_DIR
SERVICE_MODE=system|user
SERVICE_NAME
HEALTH_URL
HEALTH_ATTEMPTS
HEALTH_INTERVAL_SECONDS
HEALTH_TIMEOUT_SECONDS
MIGRATION_COMMAND
```

## 7. SSH 密钥引导

在用户批准的安全环境中生成专用密钥，例如：

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ./doctor_bill_deploy_key
```

然后：

1. 私钥内容存入 GitHub secret，完成后从本地安全删除。
2. 公钥追加到服务器部署用户 `~/.ssh/authorized_keys`。
3. 获取并人工核对服务器 host key，保存为 `DEPLOY_KNOWN_HOSTS`。
4. 测试最小权限 SSH 登录。
5. 限制部署用户只能访问项目和所需服务；需要 sudo restart 时配置精确命令白名单，不能授予宽泛免密 sudo。

不得在仓库、日志、截图或测试报告中泄露密钥。

## 8. main push 自动部署流程

模板见 `assets/github/deploy-main.yml` 和 `assets/deploy/deploy.sh`。流程必须是：

1. 仅在 `main` push 或人工触发时运行。
2. 使用 `permissions: contents: read`。
3. 使用 concurrency group 和 job timeout，避免同一环境并发部署或无限挂起。
4. 配置 SSH 私钥和 known_hosts，并启用 BatchMode、连接超时和 keepalive。
5. 连接服务器并检查项目目录、分支和工作树。
6. 工作树不干净时中止，不覆盖服务器人工修改。
7. 记录部署前 commit。
8. fetch 并 `pull --ff-only` 更新 main。
9. 使用项目既定工具同步依赖；uv 项目优先 `uv sync --frozen`。
10. 只有用户明确批准时执行 migration 命令。
11. 重启 systemd system/user service。
12. 循环调用真实健康接口。
13. 失败时采集 status/journal，回滚到部署前 commit，按旧锁文件重新执行 `uv sync --frozen` 或 `npm ci`，再重启和复检。
14. 分项报告 Git reset、依赖恢复、服务重启和健康复检状态；任一步失败必须标记 `CRITICAL`，不得用 `|| true` 隐藏。

## 9. 数据库迁移门禁

- 自动部署默认不自行生成迁移。
- migration 必须提前在开发/测试环境验证，并有备份和回滚策略。
- 破坏性 DDL、长时间锁表、大表回填和不可逆迁移不得直接随 main 自动执行。
- 优先 expand → migrate/backfill → contract 的兼容迁移顺序。
- `MIGRATION_COMMAND` 为空时跳过迁移；非空表示用户明确配置，但工作流仍应记录执行结果。

## 10. 回滚

回滚至少考虑：

- 代码 commit。
- 依赖锁文件。
- 配置兼容性。
- 数据库 schema 是否允许旧代码运行。
- 静态资源和缓存。

部署脚本只在确认服务器工作树干净后才能使用 Git 回滚。若数据库迁移不可逆，不能假装代码回滚即可恢复，必须按单独的数据恢复方案执行。

## 11. “热更新”边界

本 Skill 中“main push 热更新并重启”表示：

```text
推送 main → 自动拉取 → 同步依赖 → 可选迁移 → 重启 → 健康检查
```

它不保证严格零停机。需要零停机时，必须另行设计：

- 多实例滚动更新。
- 蓝绿部署。
- 反向代理摘流和 readiness。
- 数据库前后版本兼容。

## 12. 运维测试

测试顺序：

1. unit 文件静态检查和占位符检查。
2. 临时目录安装测试。
3. `systemd-analyze verify`（环境支持时）。
4. user/system 启停测试。
5. main push workflow 语法与 dry-run 审查。
6. 测试环境 SSH 部署、健康失败和回滚演练。
7. 生产部署后真实冒烟测试。

测试 Agent 只测试，不修改被测 unit、workflow 或部署脚本；发现问题交给开发 Agent。

## 13. 交付报告

报告服务器/用户、sudo/linger、unit 路径、WorkingDirectory、ExecStart、EnvironmentFile、重启阈值、健康窗口、SSH/secrets 名称、项目目录、部署 commit、迁移、日志、回滚、测试结果、未测范围和风险。
