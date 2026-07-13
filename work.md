# Doctor Bill Work Knowledge

旧版 `work.md` 保留为兼容导航，不删除。

有效技术知识已迁移到：

- `skills/doctor-bill-software/SKILL.md`
- `skills/doctor-bill-software/references/software-architecture.md`
- `skills/doctor-bill-hardware/SKILL.md`
- `skills/doctor-bill-hardware/references/hardware-iot.md`
- `skills/doctor-bill-ai/SKILL.md`
- `skills/doctor-bill-ai/references/ai-architecture.md`
- `skills/doctor-bill-ops/SKILL.md`
- `skills/doctor-bill-ops/references/systemd-github-actions.md`
- `references/legacy-work-knowledge.md`

继续保留的默认偏好：

- Python 3.11+，uv 优先。
- FastAPI + asyncio + lifespan。
- SQLAlchemy 2.x ORM + async engine + async_sessionmaker。
- aiohttp，不用 requests 写异步服务对外请求。
- aiomqtt，不用 paho-mqtt 写异步 MQTT 服务。
- Redis 使用新版异步客户端。
- Python 3.11+ `asyncio.TaskGroup`。
- Dify、LangChain 当前版本、RAG/Agent/微调/推理需要先查官方文档。
- Vue 3 + Vite，图表优先 ECharts。
- 运维先检查环境和权限，无 sudo 时优先 systemd user service。

注意：本文件不再承载完整流程。执行时以 `SKILL.md` 和领域 Skill 为准。
