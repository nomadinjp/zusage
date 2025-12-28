# Z.AI API 配额查询工具

一个友好的命令行工具，用于查询 Z.AI API 的 token 使用情况和配额信息。

## 功能特性

- 🎨 彩色终端输出，直观易读
- 📊 显示 token 使用百分比和进度条
- ⏰ 显示下次重置时间和剩余时间
- 📈 显示各服务（search-prime、web-reader、zread）的使用详情
- 🚀 仅依赖 Python 标准库，无需额外安装
- ⚡ 根据使用量自动变色（绿色 < 50%，黄色 50-80%，红色 > 80%）

## 安装

1. 确保 Python 3.6+ 已安装：
```bash
python3 --version
```

2. 克隆或下载 `zusage.py` 到本地

## 配置

设置环境变量 `ZAI_TOKEN`（可以从 z.ai 网站的开发者工具中获取）：

### 临时设置（当前会话）
```bash
export ZAI_TOKEN="your-authorization-token-here"
```

### 永久设置（推荐）

**对于 Bash 用户**：
```bash
echo 'export ZAI_TOKEN="your-authorization-token-here"' >> ~/.bashrc
source ~/.bashrc
```

**对于 Zsh 用户**：
```bash
echo 'export ZAI_TOKEN="your-authorization-token-here"' >> ~/.zshrc
source ~/.zshrc
```

## 使用方法

```bash
# 确保已设置 ZAI_TOKEN 环境变量
python3 zusage.py

# 或者直接执行（如果设置了执行权限）
./zusage.py
```

## 输出示例

```
🤖 Z.AI API 配额使用情况

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Token 使用情况:
  已使用: ████████░░░░░░░░░░░░ 29% (11,864,874 / 40,000,000)
  剩余: 28,135,126 tokens

⏰ 下次重置: 2025-12-28 12:33:15
  (还有 5 天 3 小时)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 各服务使用详情:
  • search-prime    0 tokens
  • web-reader      0 tokens
  • zread           0 tokens
```

## 错误处理

如果未设置 `ZAI_TOKEN` 环境变量，脚本会提示你如何设置：

```
错误: 未找到 ZAI_TOKEN 环境变量

请设置环境变量:
  export ZAI_TOKEN="your-token-here"

或者添加到 ~/.bashrc 或 ~/.zshrc:
  echo 'export ZAI_TOKEN="your-token-here"' >> ~/.bashrc
```

## 技术细节

- **语言**: Python 3
- **依赖**: 仅使用标准库（`os`, `sys`, `json`, `urllib`, `datetime`）
- **API**: `https://api.z.ai/api/monitor/usage/quota/limit`
- **认证**: Bearer Token
