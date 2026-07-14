---
name: doctor-bill-software
description: Doctor Bill 软件领域 Skill。用于产品场景、Web、API、异步 Python、数据库、报表、ECharts、前端和软件测试设计；必须由 doctor-bill 主 Skill 的需求、架构、分支和验收门禁编排。
---

# Doctor Bill Software

## 1. 调用边界

- 执行身份始终是 `super_bill`，公开品牌是贝尔 / Doctor Bill。
- 本 Skill 只负责软件领域分析和实现规则，不能绕过主 `doctor-bill`。
- 正式需求先用 `superpowers`；架构与版本选型先用 `Context7`；涉及 UI 必须用 `ui-ux-pro-max-skill`。
- 没有小白可读的需求/架构文档和用户批准，禁止写生产代码。
- 开发必须在非 `main` 分支；开发完成后交给独立测试 Agent。

## 2. 能力范围

- 产品需求、业务流程、后台、管理端、数据大屏和报表。
- Python 异步服务、FastAPI、API 契约、任务调度、消息处理。
- MySQL/PostgreSQL、SQLAlchemy ORM、Redis、数据建模与迁移。
- Vue 3、Vite、TypeScript、ECharts 和前后端联调。
- FastMCP `streamable-http` 服务、IoT 桥梁服务和 AI 应用后端。
- 高并发、高可用、链路追踪、日志、指标、告警和工程规范。

## 3. 技术选择原则

优先级：

```text
用户明确要求
> 现有项目约束
> 当前官方兼容性和安全要求
> super_bill 默认偏好
```

默认偏好，不得写成所有项目绝对要求：

- Web/API：FastAPI + asyncio + lifespan，并使用 Pydantic v2 做输入输出校验。
- Python：3.11+，适用时使用 `asyncio.TaskGroup` 和结构化并发。
- 对外 HTTP：aiohttp；现有项目已统一使用 httpx 等方案时遵循现有架构。
- 定时任务：异步 APScheduler；分布式或高可靠任务按需求评估 Taskiq/Celery/队列方案。
- Redis：redis-py 异步客户端。
- MQTT：现有架构兼容时优先 `aiomqtt`。
- PostgreSQL 驱动：psycopg 3 异步能力。
- MySQL 驱动：现有项目兼容时优先 `asyncmy`；engine、连接池和 session factory 由 lifespan 管理。
- 前端：Vue 3 + Vite；新建强类型项目优先 TypeScript，现有 JavaScript 项目遵循原架构。
- 图表：ECharts。
- Python 依赖管理：uv。

选择前必须用 Context7 核对当前版本 API、生命周期、弃用项和兼容性。

## 4. 数据库强制规则

除非用户明确指定其他方案架构，业务数据库必须遵守：

1. 使用 SQLAlchemy 2.x ORM，不能默认用裸 SQL、同步 ORM 或另一套 ORM 替代。
2. 使用 async engine、`async_sessionmaker` 和 `AsyncSession`。
3. engine 与 session factory 必须在应用 lifespan 中创建和释放。
4. Redis、aiohttp ClientSession、scheduler、MQTT client 等共享资源也应由 lifespan 统一管理。
5. 具体 `AsyncSession` 必须请求级或任务级隔离，禁止全局共享同一个 session。
6. 使用异步依赖或异步上下文管理器获取 session。
7. 事务必须有明确 commit/rollback 边界；异常时回滚并保留可追踪日志。
8. 不把 session、连接或事务跨并发任务共享。
9. 服务器现有 MySQL 且满足需求时优先复用，不擅自新建另一套数据库服务。
10. 开发数据库与测试数据库必须物理或逻辑隔离，禁止自动化测试写入开发库、生产库。

偏离这些规则时，必须引用用户明确指定的架构决定，记录原因、风险和迁移影响；“Agent 认为不兼容”不是自行绕开的理由。

## 5. 三范式与可扩展性

业务主数据默认遵循第三范式：

- 一列一个语义，避免数组字符串和重复列组。
- 非主属性依赖主键，不把多个业务实体混在一张表。
- 字典、设备、来源、用户、协议等稳定实体独立建模。
- 使用主键、外键、唯一约束和检查约束表达数据关系。
- 命名、类型、单位、精度、时区和 null 语义必须明确。

报表性能允许：

- 小时/日/月聚合表。
- 物化视图、缓存或受控冗余。
- 面向查询的宽表。

前提：

- 规范化原始数据仍然保留。
- 聚合逻辑有版本。
- 聚合结果可以从原始数据重新计算。
- 冗余字段有来源、刷新策略和一致性说明。
- 新字段和协议演进保持向后兼容。

## 6. 场景设计：先效果，再反推数据

以“查看昨日数据报告”为例，开发前必须确认：

### 展示

- 昨日属于哪个时区。
- 展示指标卡、折线图、柱状图、表格、异常列表还是导出。
- 用户需要总览、按设备、按区域、按小时还是原始明细。
- 空数据、不完整数据、延迟数据和错误如何显示。

### 消费端

假设生产端每 3 分钟上报一次，理论上每小时 20 个样本，必须确认：

- 小时值使用平均值、总和、最大、最小、最后值还是其他业务公式。
- 去重后的有效样本数是否必须等于 20。
- 缺少样本时显示现有聚合、标记不完整还是不出结果。
- 小时边界和夏令时如何处理。
- 迟到事件进入后是否重算小时值。
- 重复上报根据设备 ID、事件时间、序列号还是业务键去重。
- 历史聚合修订是否保留版本和更新时间。

### 推荐数据层次

```text
source/device
→ raw_event
→ normalized_measurement
→ hourly_aggregate
→ API DTO
→ UI
```

原始事件表示例字段：

- `id`
- `source_id` / `device_id`
- `event_time`
- `received_at`
- `sequence_no`
- `protocol_version`
- `payload_raw`
- `payload_hash`
- `quality_status`
- `created_at`

标准化测量表示例字段：

- `id`
- `raw_event_id`
- `metric_code`
- `value`
- `unit`
- `event_time`
- `quality_status`
- `parser_version`

小时聚合表示例字段：

- `id`
- `entity_id`
- `metric_code`
- `window_start`
- `timezone`
- `sample_count`
- `expected_count`
- `missing_count`
- `sum_value`
- `avg_value`
- `min_value`
- `max_value`
- `last_value`
- `completeness`
- `aggregation_version`
- `calculated_at`
- `source_updated_at`

具体字段必须根据业务确认，不能机械照抄示例。

## 7. 数据时间与兼容性

- 区分事件时间、设备时间、接收时间、入库时间和处理时间。
- 数据库统一时区策略，API 明确时区，UI 明确展示时区。
- API 新增字段优先保持可选和向后兼容；删除、重命名或改变语义必须版本化。
- 原始 payload 保留协议版本；解析器升级后能够重放和重算。
- 聚合公式、阈值和时间窗口必须配置化并记录版本。
- 数据保留、归档和删除策略必须获得用户确认。

## 8. API 设计

- 先从 UI 查询和业务动作推导 API，不按数据库表机械生成接口。
- 明确路径、方法、鉴权、权限、请求、响应、错误码、幂等和分页。
- 时间范围采用明确格式和时区，限制最大窗口，防止无界查询。
- 返回单位、精度、枚举、null 和数据完整性标志。
- 外部调用设置连接/读取/总超时、重试、退避和熔断边界。
- 日志携带 request/trace/correlation ID，不记录密钥和完整敏感 payload。
- Bearer API Key 与 OAuth2/JWT 是不同方案，必须按实际鉴权语义选择，不能只因请求头相同就混为一谈。
- 禁止在代码中写死生产 URL、密钥和环境参数。

## 9. 生命周期与并发

推荐 FastAPI 生命周期结构：

- lifespan 启动：创建 engine、session factory、Redis、aiohttp session、scheduler、消息客户端。
- lifespan 退出：停止接收、等待任务、关闭 scheduler/client/session/engine。
- 请求只获取独立 session；后台任务自行创建 session。
- 并发任务使用 TaskGroup 时定义失败传播、取消和清理语义。
- 阻塞 I/O 不得直接占用事件循环；明确线程池或进程池边界。
- 限制连接池、并发量、队列长度和批量大小，禁止无限创建任务。

## 10. 配置与工程结构

- `.env` 放项目根目录并加入忽略，不提交真实值。
- 提供 `.env.example`，只写变量名、安全示例和说明。
- 环境变量必须集中定义、类型校验并有启动失败提示。
- 区分开发、测试、预发布和生产配置。
- 禁止测试默认连接生产数据库、生产 Redis 或真实付费第三方服务。
- 代码分层应清楚区分 API、service/use case、domain、repository、models、schemas 和 integrations；是否采用完整分层取决于项目规模。
- 公开接口和核心业务代码使用类型标注；异步资源优先 `async with`；数据库模型、DTO 和业务对象边界清楚。

## 10.1 典型软件链路

以下是物联网硬件到 AI 的能力模式，不是未经需求确认就套用的固定架构：

```text
硬件设备 → MQTT → aiomqtt 桥梁 → FastAPI → SQLAlchemy async ORM → MySQL
```

```text
MQTT/HTTP 数据 → FastAPI → 数据库
                       ↔ FastMCP streamable-http → AI/Agent
```

- FastMCP 对接前必须用 Context7 核对当前导入方式、传输模式和生命周期 API。
- MQTT client、FastMCP、数据库和 HTTP client 由 lifespan 统一创建和关闭。
- 消息队列或后台作业需要异步分布式执行时可评估 Taskiq，但必须先确认可靠性和现有基础设施。
- 用户身份场景评估 OAuth2 + JWT；机器调用可能使用 Bearer API Key。必须向用户明确二者语义，不能混用。

## 11. UI 与报表

涉及 UI 必须先使用 `ui-ux-pro-max-skill`：

- 从用户任务和信息层级确定布局，不先选组件再拼页面。
- ECharts 适合趋势、对比和分布；精确查数、审计和大量明细优先表格。
- 图表必须有单位、时区、图例、tooltip、空数据和异常说明。
- 后端提供图表需要的稳定 DTO，不让前端重新猜业务聚合公式。
- 大数据量使用分页、下采样、聚合或异步导出，禁止一次拉取全部原始数据。

## 12. 可观测性和高可用

根据项目规模设计：

- 结构化日志、trace ID、指标、慢查询和错误分类。
- 健康检查区分进程存活与关键依赖就绪。
- 外部依赖超时、重试、熔断、降级和幂等。
- 定时任务防重入、分布式锁、misfire 和失败补偿。
- 数据采集链路记录来源、延迟、丢弃、重复和重试指标。
- 微服务不是默认答案；只有边界、独立扩缩容或团队所有权确实需要时才拆分。

## 13. 软件测试

顺序：单元 → 集成 → 真实 E2E。

必须覆盖：

- SQLAlchemy 模型、约束、事务和迁移。
- 开发库与测试库隔离验证。
- 聚合公式、20 样本完整小时、缺样本、重复、乱序、迟到和跨日边界。
- API 鉴权、错误、分页、时区、空值和兼容性。
- lifespan 启停与资源释放。
- API E2E 使用 `asyncio + httpx.AsyncClient` 请求真实运行服务，禁止 mock。

测试 Agent 只测试，不得为了通过测试修改本 Skill 所约束的生产代码。

## 14. 交付报告

报告技术选择及版本依据、API、数据表/字段/索引/迁移、开发/测试库、聚合语义、时区、窗口、阈值、超时、重试、并发限制、配置位置、测试结果、未测范围和风险。
