# QuecPython 基于豆包 Websocket 的 AI 对话

## 目录

- [QuecPython 基于豆包 Websocket 的 AI 对话](#quecpython-基于豆包-websocket-的-ai-对话)
  - [目录](#目录)
  - [介绍](#介绍)
  - [功能特性](#功能特性)
  - [快速开始](#快速开始)
    - [先决条件](#先决条件)
    - [安装](#安装)
    - [运行应用程序](#运行应用程序)
  - [目录结构](#目录结构)
  - [贡献](#贡献)
  - [许可证](#许可证)
  - [支持](#支持)

## 介绍

QuecPython 推出了基于豆包 Websocket 的 AI 聊天解决方案。该方案基于火山的 Websocket 接口，实现语音对话。

支持该功能的模组型号如下：

| 系列   | 型号        |
| :----- | :---------- |
| EC800M | EC800MCN_LE |

## 功能特性

- 支持语音一问一答。
- 支持独立 ASR 语音识别。
- 支持独立 TTS 播放。
- 支持独立大模型问答。
- 使用 Python 语言，便于二次开发。

## 快速开始

### 先决条件

在开始之前，请确保您具备以下先决条件：

- **硬件：**
  - [EC800MCNLE QuecPython 标准开发板](https://python.quectel.com/doc/Getting_started/zh/evb/ec800x-evb.html)（含天线、Type-C 数据线等）
    
    > - 点击查看开发板的[原理图](https://python.quectel.com/wp-content/uploads/2024/09/EC800X_EVB_V1.1-SCH.pdf)和[丝印图](https://python.quectel.com/wp-content/uploads/2024/09/EC800X%E7%B3%BB%E5%88%97%E5%BC%80%E5%8F%91%E6%9D%BF%E4%B8%9D%E5%8D%B0.pdf)文档。
    > - [移远商城购买链接](https://www.quecmall.com/goods-detail/2c90800c94028da201944df5ed4e0091)
    
  - 电脑（Windows 7、Windows 10 或 Windows 11）
  
  - 喇叭
    - 任意 2-5W 功率的喇叭即可
    - [移远商城购买链接](https://www.quecmall.com/goods-detail/2c90800c94028da201948249e9f4012d)
  
- **软件：**
  - QuecPython 模块的 USB 驱动：[QuecPython_USB_Driver_Win10_ASR](https://images.quectel.com/python/2023/04/Quectel_Windows_USB_DriverA_Customer_V1.1.13.zip)
  - 调试工具 [QPYcom](https://images.quectel.com/python/2022/12/QPYcom_V3.6.0.zip)
  - QuecPython [固件](https://github.com/QuecPython/AIChatBot-Volcengine-webRTC/releases/download/v1.0.0/EC600MCNLER06A01M08_OCPU_QPY_TEST0213.zip)
  - Python 文本编辑器（例如，[VSCode](https://code.visualstudio.com/)、[Pycharm](https://www.jetbrains.com/pycharm/download/)）

### 安装

1. **克隆仓库**：
   
   ```bash
   git clone https://github.com/QuecPython/AIChatBot-Volcengine-websocket.git
   cd AIChatBot-Volcengine-websocket
   ```
   
2. **安装 USB 驱动**

3. **烧录固件：**
   按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#%E4%B8%8B%E8%BD%BD%E5%9B%BA%E4%BB%B6)将固件烧录到开发板上。

> 如需使用，请先通过`tiktok.config`接口更新火山 token等参数再进行使用。

### 运行应用程序

1. **连接硬件：**
   按照下图进行硬件连接：
   <img src="./docs/zh/media/wire_connection.jpg" style="zoom:67%;" /> 
   1. 将喇叭连接至图中标识有`SPK+`和`SPK-`的排针上。
   3. 在图示位置插入可用的 Nano SIM 卡。
   4. 将天线连接至标识有`LTE`字样的天线连接座上。
   5. 使用 Type-C 数据线连接开发板和电脑。
2. **将代码下载到设备：**
   - 启动 QPYcom 调试工具。
   - 将数据线连接到计算机。
   - 按下开发板上的 **PWRKEY** 按钮启动设备。
   - 按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#%E4%B8%8B%E8%BD%BD%E8%84%9A%E6%9C%AC)将 `code` 文件夹中的所有文件导入到模块的文件系统中，保留目录结构。

> 注意： 如果需要提高mic的灵敏度，避免说话识别错误，请将 nvm 文件夹下的 audio_gain.nvm 和 audio_ve.nvm 文件导入到模块文件系统的 /usr 目录中。

3. **运行应用程序：**
   - 通过`TiktokWS.config`方法更新参数。
   - 选择 `File` 选项卡。
   - 选择 `tiktok_websocket_demo.py` 脚本。
   - 右键单击并选择 `Run` 或使用`运行`快捷按钮执行脚本。
4. **参考运行日志：**
```python
>>>from usr.tiktokws import TiktokWS
>>>tiktok=TiktokWS()
>>>tiktok.config(ModelId='ep-20250108223254-x4r5r')
True

# 选择tiktok_websocket_demo.py脚本右键单击运行
>>>example.exec('/usr/tiktok_websocket_demo.py')
ai start success...
please press KEY S2 to start

# 按住KEY S2键开始说话
>>> please speak to ai.

# 松开KEY S2键停止说话,随后喇叭播放回复音频
speak over and wait ai response.
```

## 目录结构

```plaintext
solution-AI/
├── code/
│   ├── ark_lib.py
│   ├── asr_lib.py
│   ├── logging.py
│   ├── ...
│   └── uwebsocket.py
├── photo/
│   └── wire_connection.jpg
├── fw/
│   └── EC800MCNLER06A01M08_OCPU_QPY_TEST0228.zip
├── LICENSE
└── readme.md
```

## 贡献

我们欢迎对本项目的改进做出贡献！请按照以下步骤进行贡献：

1. Fork 此仓库。
2. 创建一个新分支（`git checkout -b feature/your-feature`）。
3. 提交您的更改（`git commit -m 'Add your feature'`）。
4. 推送到分支（`git push origin feature/your-feature`）。
5. 打开一个 Pull Request。

## 许可证

本项目使用 Apache 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

## 支持

如果您有任何问题或需要支持，请参阅 [QuecPython 文档](https://python.quectel.com/doc) 或在本仓库中打开一个 issue。