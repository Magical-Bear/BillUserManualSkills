---
name: doctor-bill-ai
description: Doctor Bill AI 领域 Skill。用于 Dify、RAG、Agent、LangChain/LangGraph、FastMCP、模型推理、微调、评估、多模态和 AI 数据治理；必须由 doctor-bill 主 Skill 编排。
---

# Doctor Bill AI

## 1. 调用边界

- 执行身份是 `super_bill`，品牌是贝尔 / Doctor Bill。
- 本 Skill 不能绕过主 Skill 的需求、Context7、分支、独立测试和用户验收门禁。
- AI 产品有 UI、API、数据库或部署时，同时使用软件、UI 和运维领域规则。

## 2. 能力范围

- Dify 工作流、知识库、工具、应用发布和 API 集成。
- LangChain 以 Context7 查到的当前稳定 API 为准，不沿用旧版 Agent 创建和中间件接口。
- LangChain/LangGraph、RAG、Agent、工具调用和结构化输出。
- FastMCP，默认优先当前官方支持的 HTTP 传输模式并通过 Context7 核对。
- embedding、reranker、向量数据库、索引和检索策略。
- Hugging Face、PyTorch、ms-swift、SFT/LoRA/QLoRA、数据准备、训练、评估和推理。
- vLLM 等推理服务、量化、批处理、并发和显存规划。
- ASR、TTS、图像、多模态和流式交互。

不把某个框架或模型写成绝对选择。先按用户要求、现有架构、当前官方文档、安全和成本选型。

## 3. AI 需求必须量化

需求文档必须说明：

- 用户任务、成功定义和不允许发生的结果。
- 输入输出格式、语言、上下文长度和响应方式。
- 准确率/召回率/引用正确性/结构化输出成功率等指标。
- 首 token 延迟、总延迟、吞吐、并发和可用性。
- 单次、每日和峰值成本预算。
- 隐私、数据保留、模型供应商和地域限制。
- 人工审核、拒答、降级和兜底流程。

“接一个大模型”不是完整需求。

## 4. 架构和版本研究

正式选型前必须使用 Context7 查询当前官方文档，确认：

- SDK/API 当前版本和弃用项。
- 同步/异步能力、流式协议、重试和超时。
- 模型上下文、结构化输出、工具调用和多模态限制。
- Dify/LangChain/LangGraph/FastMCP 的当前接口。
- 向量数据库过滤、索引和一致性能力。
- 推理框架的模型、量化和硬件兼容性。

输出候选方案、选择理由、版本依据、迁移风险和替代方案。

## 5. RAG 数据链路

从最终回答效果反推：

```text
业务来源
→ 采集/同步
→ 原始文档
→ 解析/清洗
→ 切分
→ embedding
→ 索引
→ 检索/过滤
→ rerank
→ prompt/context
→ 模型回答
→ 引用与评估
```

必须版本化：

- source/document version
- parser version
- chunking version
- embedding model/version
- index version
- retrieval configuration version
- reranker version
- prompt version
- model/provider version

保留原始文档和来源元数据，使索引可以重建。删除或权限变化必须传播到 chunk、索引、缓存和回答层。

## 6. AI 数据存储

软件数据库规则仍然适用：默认 SQLAlchemy async ORM、lifespan 管理 engine/session factory、请求/任务 session 隔离、三范式、开发/测试库分离。

建议分离：

- 业务实体和权限。
- 原始文档和来源。
- 文档版本和解析结果。
- chunk 元数据。
- 索引/embedding 版本映射。
- prompt/model/config 版本。
- 运行 trace、token、成本和延迟。
- 评估数据集、期望结果和评估运行。
- 用户反馈、人工审核和缺陷标签。

向量不应成为唯一数据源；必须能够根据原始文档和版本信息重建。

## 7. Agent 与工具调用

- 工具 schema 明确类型、必填、枚举、错误和幂等语义。
- 高风险工具使用最小权限、确认、审计和可撤销设计。
- 不把模型文本直接拼接为 SQL、Shell 或权限操作。
- 工具超时、重试、熔断、并发和预算必须有限制。
- Agent 循环设置最大步骤、最大时间、最大 token/成本和终止条件。
- 保存 trace，但脱敏密钥、个人数据和敏感内容。
- 结构化输出必须做 schema 校验和失败重试/降级，不能只相信模型格式。

## 8. Prompt 和模型管理

- prompt 不散落在代码中；集中管理、版本化并记录变量。
- system、developer、user、tool 内容边界清楚，外部内容视为不可信输入。
- 防范 prompt injection、数据外泄和越权工具调用。
- 模型变更必须重新跑评估，不以主观体验替代指标。
- 供应商、模型名、温度、top_p、max tokens、超时、重试和并发均配置化。
- 需要稳定输出时优先使用结构化响应和低随机性，但以具体任务评估为准。

## 9. 微调与训练

开发前确认：

- 基础模型许可、数据许可和商用限制。
- 训练目标是否真的需要微调，能否通过 RAG、工具或 prompt 解决。
- 训练/验证/测试数据按来源或时间隔离，防止泄漏。
- 去重、清洗、PII、版权和危险内容处理。
- 超参数、随机种子、代码、数据快照和 checkpoint 可复现。
- 基线模型和微调模型使用同一评估集比较。
- 上线、灰度、回滚和旧版本保留。

## 10. 推理与容量

Linux 自托管场景可优先评估 vLLM，但必须按当前兼容性确认。量化并报告：

- GPU 型号、显存、数量和拓扑。
- 模型参数、dtype/量化、上下文和 KV cache。
- 最大并发、batch/token 策略、吞吐和延迟。
- 请求队列、限流、超时、取消和背压。
- 多副本、健康检查、模型加载时间和滚动策略。
- 降级模型、供应商回退和成本边界。

## 10.1 典型多模态客户端

历史能力模式：

```text
唤醒词检测 → 录音 → ASR 转文本
                    ↓
拍照 → 图像 + 文本 → Dify/Agent → 流式返回
                    ↓
              流式解析 → TTS 播放
```

实现前仍需确认设备、音频、相机、模型、延迟、隐私和离线降级，不能只复制历史项目。

## 11. 多模态链路

例如：

```text
唤醒词 → ASR → 图像/文本理解 → Dify/Agent → 流式响应 → TTS
```

必须分别定义：

- 音频格式、采样率、VAD、语言和噪声条件。
- 图像尺寸、压缩、隐私和保留周期。
- 中间结果、时间戳、取消和会话状态。
- 首包/首 token/首音频延迟目标。
- ASR、模型、工具、TTS 任一失败时的降级。

## 12. 评估与测试

测试顺序：单元 → 集成 → 离线评估 → 真实 E2E → 上线观测。

至少覆盖：

- 固定评估集与不可见测试集。
- 检索 recall@k、MRR/nDCG 或业务指标。
- 回答正确性、引用支持度、拒答和越权。
- 结构化输出成功率和工具调用成功率。
- prompt injection、敏感信息和权限隔离。
- 延迟、并发、token、成本、超时和降级。
- 模型/embedding/prompt/index 版本回归。

E2E 必须请求真实运行的 AI 服务和 API；如果因成本或密钥不能执行，明确列出，不得用 mock 结果冒充。

测试 Agent 只测试，不修改生产 AI 流程或 prompt 来让结果通过。

## 13. 交付报告

报告模型/供应商、框架和版本、数据来源、索引与 prompt 版本、指标、阈值、延迟、并发、token/成本预算、安全边界、配置位置、评估结果、未测范围、风险和回滚方式。
