# systemd and GitHub Actions Deployment Reference

## 目录

1. systemd system service
2. systemd user service and linger
3. GitHub Actions SSH 部署
4. 健康检查
5. 回滚
6. 配置变量

## 1. systemd system service

适用于有 sudo 且用户批准的服务器。unit 要写清楚工作目录、启动命令、环境文件、用户、重启策略、超时、依赖和日志。

## 2. systemd user service and linger

无 sudo 时使用：

```text
~/.config/systemd/user/<service>.service
systemctl --user daemon-reload
systemctl --user enable --now <service>
```

检查 linger：

```text
loginctl show-user <user> -p Linger
```

若为 no，需要管理员执行：

```text
sudo loginctl enable-linger <user>
```

当前无 sudo 用户不要伪装已启用。

## 3. GitHub Actions SSH 部署

Secrets 建议：

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`
- `DEPLOY_PATH`
- `DEPLOY_SERVICE`
- `HEALTHCHECK_URL`

Actions 需要 `concurrency`，checkout 后配置 SSH，写入 known_hosts，SSH 到服务器执行部署脚本。

服务器命令建议：保存当前 revision → fetch main → checkout/reset 到目标 revision → `uv sync` → 执行批准的迁移 → 重启服务 → 健康检查。失败时恢复上一 revision、重启、再次健康检查并输出 journal。

## 4. 健康检查

健康检查必须请求真实接口，不只看进程存在。需要明确 URL、超时、重试、间隔、成功状态码和期望响应片段。

## 5. 回滚

回滚策略至少包含：上一 revision、依赖锁文件、迁移兼容性、静态资源、服务重启和回滚后健康检查。破坏性数据库迁移必须先做备份和回滚演练。

## 6. 配置变量

常见位置：`.env.example`、systemd EnvironmentFile、GitHub Actions Secrets、README 部署章节。

关键变量：

- `DEPLOY_PATH`
- `DEPLOY_SERVICE`
- `HEALTHCHECK_URL`
- `HEALTHCHECK_TIMEOUT_SECONDS`
- `HEALTHCHECK_RETRY_ATTEMPTS`
- `HEALTHCHECK_RETRY_INTERVAL_SECONDS`
- `SYSTEMD_RESTART_SEC`
- `SYSTEMD_TIMEOUT_START_SEC`
- `SYSTEMD_TIMEOUT_STOP_SEC`
