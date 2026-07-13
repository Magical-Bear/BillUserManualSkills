---
name: doctor-bill-ops
description: Doctor Bill 运维领域 Skill。负责 Linux、systemd、linger、无 sudo 部署、GitHub Actions SSH 发布、健康检查和回滚。
allowed-tools: Read, Write, Edit, Bash
---

# Doctor Bill Ops

用于 Linux、systemd、linger、部署、GitHub Actions、日志、监控、健康检查和回滚。主入口仍是 `doctor-bill`。

## systemd 规则

- 有 sudo 且用户批准时可以设计 system service。
- 无 sudo 时优先 systemd user service：`~/.config/systemd/user/` + `systemctl --user`。
- 必须检测 linger：`loginctl show-user <user> -p Linger`。
- 当前用户无法启用 linger 时，明确给管理员命令，禁止绕权限。
- unit 必须明确 `WorkingDirectory`、`ExecStart`、`EnvironmentFile`、`Restart`、`RestartSec`、`TimeoutStartSec`、`TimeoutStopSec`、日志查看方式。
- 部署后检查 `systemctl status`、`journalctl` 和真实健康接口。

## GitHub Actions main push SSH 部署

必须设计：

- 专用 SSH key，不复用个人主密钥。
- `known_hosts`，禁止默认关闭主机校验。
- Secrets：host、port、user、key、项目目录、服务名、健康接口等。
- main push 触发。
- concurrency 并发锁，避免重复部署。
- SSH 到服务器后进入项目目录，拉取 main，`uv sync`，执行已批准迁移，重启服务，健康检查。
- 失败采集日志并回滚到上一个已知可用版本。
- 最小权限部署用户。

## 自动重启 ≠ 零停机

systemd restart 和 GitHub Actions 自动重启只能说明自动更新并恢复服务，不等于严格零停机。需要零停机时必须另行设计蓝绿、滚动、反向代理切流或双实例健康探测。

更多细节见 `references/systemd-github-actions.md`。
