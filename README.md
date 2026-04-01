# colleague-beier

> 贝尔 - 全栈工程师 AI Skill

将同事"贝尔"的技术能力和性格蒸馏成可调用的 Claude Code Skill。

## 简介

**贝尔** 是一位全栈工程师，技术栈覆盖：
- 硬件: ESP32/STM32
- 后端: FastAPI + 全异步架构
- 前端: Vue3 + Vite
- AI: HuggingFace/VLLM/Dify

## 快速开始

### Claude Code 安装

```bash
# 克隆到 Claude Code skills 目录
cd ~/.claude/skills
git clone https://github.com/Magical-Bear/BillUserManualSkills.git bill
```

在 Claude Code 中调用：

```
/bill
```

### Cursor 安装

```bash
# 克隆到 Cursor rules 目录
cd ~/.cursor/rules
git clone https://github.com/Magical-Bear/BillUserManualSkills.git bill
```

在 Cursor 中使用 `@bill` 调用

## 技术特点

### 核心原则
- **全异步架构**: Python 3.11+，强制 asyncio
- **现代工具链**: UV > conda, aiohttp > requests
- **物联网**: MQTT 优先，aiomqtt 实现
- **AI 开发**: LangChain V1.0, Dify 工作流

### 典型架构

```
硬件 → MQTT → aiomqtt → FastAPI → 数据库
```

## 文件结构

```
.
├── SKILL.md          # Skill 定义和运行规则
├── work.md           # 技术能力详细说明
├── persona.md        # 性格和沟通风格
├── meta.json         # 元数据
└── README.md         # 本文件
```

## 技术栈

### 硬件
- ESP32 (MicroPython/Arduino)
- STM32 (HAL/串口通信)
- 传感器组网

### 后端
- FastAPI + asyncio
- aiomqtt, aiohttp
- SQLAlchemy, Redis, taskiq
- Pydantic v2

### 前端
- Vue 3 + Vite + JS

### AI/ML
- PyTorch + HuggingFace
- VLLM 部署
- LangChain V1.0
- Dify 工作流

## License

MIT

## Author

Magical-Bear
