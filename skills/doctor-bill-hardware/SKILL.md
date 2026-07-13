---
name: doctor-bill-hardware
description: Doctor Bill 硬件领域 Skill。负责 ESP32、STM32、传感器、串口、MQTT、固件、结构件和硬件数据链路设计。
allowed-tools: Read, Write, Edit, Bash
---

# Doctor Bill Hardware

用于 ESP32、STM32、传感器、串口、MQTT、固件、结构件和设备上报链路。主入口仍是 `doctor-bill`。

## 默认偏好

- ESP32：MicroPython 优先，Arduino 备选；如项目已有 ESP-IDF/Arduino 约束则尊重现状。
- STM32：HAL，串口常用 JSON + `\r\n` 结尾；行动前确认板型、外设、时钟、供电和调试接口。
- 传感器：红外对射、超声波、五路循迹、温湿度、环境传感、数码管、键盘、I2C。
- 设备间通信优先 MQTT；需要本地实时闭环时明确离线策略。
- 服务器间桥接优先 HTTP；实时性强时 WebSocket。

## 硬件需求必须问清

- 设备型号、MCU、固件框架、引脚、供电、电平、外设总线。
- 传感器单位、采样频率、上报频率、滤波、校准、异常值。
- 串口波特率、校验位、停止位、帧边界、重传和 CRC。
- MQTT broker、Topic、QoS、retain、clean session、离线缓存和重连策略。
- 协议版本、字段兼容、raw payload、幂等键和时间戳。
- 现场安装、结构件、线缆、抗干扰、防水、防尘和维护方式。

## 数据链路输出

必须说明：

```text
传感器/设备 → 固件协议 → 串口/MQTT/HTTP → 桥梁服务 → 原始数据表 → 标准化/聚合 → API/UI/AI
```

更多细节见 `references/hardware-iot.md`。
