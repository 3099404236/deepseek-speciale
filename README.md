# DeepSeek V3.2-Speciale CLI

[English](#english) | [中文](#中文)

> **Platform: Linux / macOS only** (Windows not supported)

---

## English

⚠️ **Temporary Version - Expires 2025-12-15**

### Why this project?

DeepSeek V3.2-Speciale is currently **not compatible with Claude Code, Codex, and similar AI coding assistants**. This CLI tool provides a simple way to access the V3.2-Speciale model directly from your terminal.

**Supported platforms:** Linux, macOS

### Features

- DeepSeek V3.2-Speciale model support
- 128K max output tokens
- Thinking process display
- Session management
- Bilingual (Chinese/English)

### Installation

```bash
git clone https://github.com/3099404236/deepseek-speciale.git
cd deepseek-speciale
pip install -r requirements.txt
./install.sh
```

### Usage

```bash
deepseeks
```

### Commands

| Command | Description |
|---------|-------------|
| `q`/`exit` | Exit |
| `clear` | Clear chat |
| `think` | Toggle thinking |
| `show` | Show thinking |
| `new` | New chat |
| `sessions` | Session menu |
| `lang` | Switch language |
| `help` | Help |

### API Pricing

- Input (cache hit): ¥0.2/M tokens
- Input (cache miss): ¥2/M tokens
- Output: ¥3/M tokens

---

## 中文

⚠️ **临时版本 - 有效期至 2025-12-15**

### 为什么做这个项目？

DeepSeek V3.2-Speciale 目前**不兼容 Claude Code、Codex 等 AI 编程助手**，所以做了这个命令行工具，方便直接在终端使用 V3.2-Speciale 模型。

**支持平台:** Linux, macOS (不支持 Windows)

### 特点

- 支持 V3.2-Speciale 模型
- 最大输出 128K tokens
- 思考过程显示
- 会话管理
- 中英文双语

### 安装

```bash
git clone https://github.com/3099404236/deepseek-speciale.git
cd deepseek-speciale
pip install -r requirements.txt
./install.sh
```

### 使用

```bash
deepseeks
```

### 命令

| 命令 | 说明 |
|------|------|
| `q`/`exit` | 退出 |
| `clear` | 清空对话 |
| `think` | 切换思考显示 |
| `show` | 查看思考过程 |
| `new` | 新对话 |
| `sessions` | 会话菜单 |
| `lang` | 切换语言 |
| `help` | 帮助 |

### API 价格

- 输入 (缓存命中): ¥0.2/百万tokens
- 输入 (缓存未命中): ¥2/百万tokens
- 输出: ¥3/百万tokens

---

## License

MIT
