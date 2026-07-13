# Software Architecture Reference

## 目录

1. 需求文档字段
2. FastAPI 资源生命周期
3. SQLAlchemy 2.x 异步模式
4. 数据建模和兼容
5. API 和 UI 报表
6. 配置变量建议

## 1. 需求文档字段

软件需求文档至少包含：背景、目标、非目标、用户角色、使用场景、展示效果、API、数据库、权限、异常处理、日志指标、部署、测试计划、验收标准、时间窗口、超时、重试和阈值。

## 2. FastAPI 资源生命周期

- lifespan 中创建 engine、session factory、Redis、aiohttp ClientSession、scheduler、MQTT client 等共享资源。
- shutdown 时按依赖反向顺序释放。
- 请求级资源通过 Depends 或 async context 管理。
- CPU 重任务走进程池；轻阻塞任务可用 `asyncio.to_thread`；多并发任务优先 `asyncio.TaskGroup`。

## 3. SQLAlchemy 2.x 异步模式

- `create_async_engine()` 创建 engine。
- `async_sessionmaker(engine, expire_on_commit=False)` 创建 session factory。
- 每个请求创建独立 `AsyncSession`。
- 写操作使用 `async with session.begin()` 或显式 commit/rollback。
- 不把 session 存全局，不跨请求复用。
- 模型使用 ORM 映射，迁移工具按项目现有方案选择。

## 4. 数据建模和兼容

建议字段：

- `id`：主键。
- `source_id`/`device_id`/`tenant_id`：来源和隔离。
- `event_time`：生产端事件时间。
- `ingested_at`：服务端入库时间。
- `protocol_version`/`schema_version`：协议版本。
- `idempotency_key`：幂等键。
- `raw_payload`：原始数据 JSON。
- `created_at`/`updated_at`：业务审计时间。

聚合表必须能由原始数据重算。受控冗余要写明重算任务、回填策略和一致性窗口。

## 5. API 和 UI 报表

API：

- 时间参数使用 ISO 8601 或明确格式。
- 查询区间默认闭开 `[start, end)`。
- 明确默认时区和自然日定义。
- 分页、排序、过滤和最大导出量写入配置。
- 错误码包含参数错误、权限不足、数据不存在、上游不可用和超限。

UI：

- 页面需要 loading、empty、error、forbidden、partial data 状态。
- ECharts 需要单位、tooltip、legend、dataZoom、异常值和延迟数据标识。
- 表格需要列定义、排序、筛选、分页和导出边界。

## 6. 配置变量建议

配置位置优先：`.env.example`、项目配置类、部署环境变量和 README。

常见变量：

- `DATABASE_URL`
- `REDIS_URL`
- `API_REQUEST_TIMEOUT_SECONDS`
- `HTTP_RETRY_ATTEMPTS`
- `REPORT_DEFAULT_WINDOW_DAYS`
- `REPORT_MAX_WINDOW_DAYS`
- `EXPORT_MAX_ROWS`
- `AGGREGATION_DELAY_SECONDS`
- `SCHEDULER_TIMEZONE`
