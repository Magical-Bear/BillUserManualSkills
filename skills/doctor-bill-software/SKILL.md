---
name: doctor-bill-software
description: Doctor Bill 软件领域 Skill。负责产品场景、前后端、API、数据库、报表、UI/ECharts、SQLAlchemy 2.x 异步 ORM 和软件开发流程。
allowed-tools: Read, Write, Edit, Bash
---

# Doctor Bill Software

用于软件、产品、后端、前端、API、数据库、报表和 UI/ECharts 任务。主入口仍是 `doctor-bill`；本 Skill 只负责软件领域细节。

## 必须遵守

- 正式需求阶段必须先由 `doctor-bill` 通过 superpowers 门禁。
- 架构分析必须用 Context7 查当前版本官方文档。
- 涉及 UI、后台、报表、大屏、ECharts、布局或视觉时必须使用 `ui-ux-pro-max-skill`。
- 开发前必须有用户批准的需求/架构文档。

## 场景自顶向下

用户只说“做一个报表/页面/API/昨日数据”时，不要直接写代码。先倒推：

1. 最终展示：谁看、看什么、时间范围、时区、指标、筛选、导出。
2. UI：页面结构、ECharts/表格、交互、空状态、错误状态、加载态。
3. 消费端：聚合口径、时间粒度、缺失/重复/延迟数据处理。
4. API：参数、响应、鉴权、错误码、分页、速率和数据量限制。
5. 数据库：原始表、业务表、聚合表、索引、三范式、兼容扩展。
6. 桥梁层：MQTT、HTTP、任务、网关、文件导入和幂等入库。
7. 生产端：字段、单位、采样频率、上报频率、协议版本、离线缓存。

输出必须还原为：

```text
生产端 → 桥梁/采集层 → 原始数据 → 标准化/聚合 → API → UI
```

## 默认技术栈

按用户批准文档优先；无明确约束时默认：

- Python 3.11+、uv。
- FastAPI、Pydantic v2。
- SQLAlchemy 2.x ORM。
- SQLAlchemy async engine + `async_sessionmaker`。
- 优先服务器已有 MySQL；已有 PostgreSQL/SQLite/其他 DB 时尊重项目约束。
- Redis 异步客户端。
- aiohttp 对外 HTTP 请求。
- FastAPI lifespan 管理共享资源。
- Python 3.11+ `asyncio.TaskGroup`。
- APScheduler 异步定时任务。
- Vue 3 + Vite。
- ECharts 数据图表。

## 数据库强制规则

- engine 和 session factory 在 lifespan 中创建和释放。
- `AsyncSession` 必须请求级隔离，禁止全局共享同一个 session。
- 使用异步依赖或异步上下文管理 session。
- transaction 必须有明确 commit/rollback 边界。
- 业务库默认第三范式。
- 报表允许聚合表或受控冗余，但必须保留规范化原始数据，聚合可重算。
- 原始数据不能被聚合结果替代。
- 协议字段必须支持向后兼容扩展：保留 raw payload、schema/protocol version、source timestamps、ingested_at、幂等键。

## API/UI 要点

- API 明确鉴权方式：Bearer API Key、OAuth2/JWT 或现有方案。
- 时间范围必须明确时区、闭开区间、默认窗口和最大窗口。
- 分页和导出要限制数据量，避免一次性扫全表。
- UI 必须定义加载、空数据、错误、权限不足和刷新状态。
- ECharts 必须定义指标单位、tooltip、legend、zoom、异常值展示和色彩语义。

## 开发交付

开发 Agent 完成后报告：修改文件、DB 表/字段/索引/迁移、配置变量、默认值、时间窗口、超时、重试、阈值位置、兼容策略、风险和需要测试 Agent 验证的场景。

更多细节见 `references/software-architecture.md`。
