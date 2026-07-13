---
name: doctor-bill-ai
description: Doctor Bill AI 领域 Skill。负责 Dify、LangChain、RAG、Agent、微调、vLLM、ASR/TTS、多模态和评估闭环。
allowed-tools: Read, Write, Edit, Bash
---

# Doctor Bill AI

用于 Dify、LangChain、RAG、Agent、微调、推理、ASR/TTS、多模态和评估。主入口仍是 `doctor-bill`。

## 必须遵守

- 架构和 API 使用前必须用 Context7 查当前官方文档。
- LangChain 不能沿用旧版 Agent 记忆，必须按当前文档确认创建方式、中间件和工具调用。
- 涉及 UI/标注台/评估后台时加载 `ui-ux-pro-max-skill`。
- 不写入密钥，不提交模型服务 Token、Dify API Key 或私有数据。

## 默认方向

- Dify：工作流、知识库、API 调用、流式响应、变量和错误分支要明确。
- RAG：文档来源、切分、embedding、索引、召回、重排、引用、权限隔离和评估集。
- Agent：工具边界、权限、审计日志、超时、重试、幂等和人工确认点。
- 微调：数据许可、样本格式、训练/验证划分、评估指标、回滚和模型卡。
- 推理：Linux 优先 vLLM；并发、显存、上下文长度、量化、批处理和限流要量化。
- 多模态：唤醒词 → ASR → 图像/文本 → Dify/Agent → 流式返回 → TTS。

## 交付要求

必须报告：模型/框架版本依据、数据来源、隐私边界、提示词/工作流变量、评估指标、失败样例、超时、重试、限流、费用风险和回滚方式。

更多细节见 `references/ai-architecture.md`。
