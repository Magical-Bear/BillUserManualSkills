# Legacy Work Knowledge Migrated from colleague-beier

## 目录

1. 基础偏好
2. 硬件与通信
3. Python 后端
4. AI 与多模态
5. 前端
6. 典型链路

## 1. 基础偏好

- 执行身份：super_bill。
- 全异步优先，现代工具链优先。
- uv 优于 conda。
- FastAPI 优于其他 Python Web 框架。
- Linux 环境 vLLM 优先，Windows 视项目条件调整。

## 2. 硬件与通信

- ESP32：MicroPython 优先，Arduino 备选。
- STM32：HAL、串口通信；串口数据常用 JSON + `\r\n` 结尾。
- 传感器：红外对射、超声波、五路循迹、温湿度、环境传感、数码管、键盘、I2C。
- 结构：铝型材、内置角码、转向角码、滑块螺母。
- 设备间通信优先 MQTT；服务器间优先 HTTP，需要实时性时 WebSocket。

## 3. Python 后端

- Python 3.11+。
- FastAPI + lifespan 管理共享资源。
- Pydantic v2。
- 对外 HTTP 使用 aiohttp。
- MQTT 使用 aiomqtt。
- Redis 使用 redis-py asyncio。
- 队列可用 taskiq。
- 认证需先明确 Bearer API Key 还是 OAuth2/JWT；除注册登录外，鉴权走异步 Depends。
- `.env` 放项目根目录；默认只创建 `.env.example`，未经用户允许不读取生产 `.env`。

## 4. AI 与多模态

- Hugging Face + PyTorch。
- 推理部署优先 vLLM。
- LangChain 必须按当前官方文档实现，不沿用旧 Agent API。
- 熟悉 Dify、LangChain、ms-swift 微调、智能体开发。
- 多模态链路：唤醒词 → 录音 → ASR → 图像/文本 → Dify 工作流 → 流式返回 → TTS。

## 5. 前端

- Vue 3 + Vite。
- 默认 JavaScript，除非项目已有 TypeScript 或用户指定。
- 数据报表和大屏优先 ECharts。

## 6. 典型链路

```text
硬件设备 → MQTT → aiomqtt 订阅 → FastAPI 后端 → 数据库
```

```text
MQTT 消息 → aiomqtt/FastAPI 转换 → 数据库/API → FastMCP 或前端消费
```
