# 慧眼视觉平台 (MiniMax Vision Frontend)

基于 Vue 3 + Flask + MiniMax API 的智能视觉对话平台，支持图片分析和流式对话。

**在线访问**: http://160.202.238.167:24066

## 功能特性

### 🖼️ 图片分析
- 支持拖拽/粘贴上传图片
- 支持 Ctrl+V 粘贴图片
- 支持 URL 图片分析
- 自动生成描述

### 💬 智能对话
- 流式输出，实时显示 AI 回复
- **支持停止按钮**，可中断生成
- 多对话历史管理
- Markdown 渲染（代码高亮、表格、列表）
- 支持附加图片到对话

### 📱 全屏模式
- 点击全屏按钮进入沉浸式对话
- 支持 ESC 键退出

### 🔒 设备隔离
- 每个浏览器设备独立存储对话
- 对话数据不与其他用户共享

## 技术架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue 3 前端    │────▶│   Flask 后端    │────▶│  MiniMax API   │
│   (端口 4000)   │◀────│  (端口 5001)   │◀────│  (天行AI代理)  │
└─────────────────┘ SSE └─────────────────┘     └─────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
# 前端依赖
npm install

# 后端依赖
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# MiniMax API Key（必须）
export MINIMAX_API_KEY="your_minimax_api_key"

# 对话 API（天行AI，必须）
export CHAT_API_KEY="your_chat_api_key"

# 外部 API 密钥（可选）
export API_KEY="your-api-key"
```

### 3. 启动后端

```bash
cd backend
python app.py
```

后端运行在 http://localhost:5001

### 4. 启动前端

```bash
npm run dev
```

前端运行在 http://localhost:4000

## API 文档

### 认证

API 使用 `X-API-Key` 请求头认证（可选）：

```bash
curl -H "X-API-Key: your-api-key" ...
```

### 端点

#### POST /api/analyze
图片分析

```bash
curl -X POST http://localhost:5001/api/analyze \
  -F "image=@photo.jpg" \
  -F "prompt=请描述这张图片"
```

#### POST /api/chat/stream
流式对话（SSE）

```bash
curl -X POST http://localhost:5001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "abc123"}'
```

**SSE 事件流格式:**
```
data: {"type": "session_id", "session_id": "abc123"}

data: {"type": "content", "content": "你好"}

data: {"type": "content", "content": "，我是"}

data: {"type": "content", "content": "AI 助手"}

data: {"type": "done"}
```

#### POST /api/chat/clear
清除会话历史

```bash
curl -X POST http://localhost:5001/api/chat/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123"}'
```

## 项目结构

```
minimax-vision-frontend/
├── src/
│   ├── api/
│   │   └── analysis.ts       # API 调用（含 AbortSignal 支持）
│   ├── components/
│   │   ├── ChatPanel.vue     # 聊天组件（Markdown/全屏/停止）
│   │   ├── ImageUploader.vue # 图片上传
│   │   └── AnalysisResult.vue
│   ├── views/
│   │   └── Home.vue          # 主视图（多对话管理）
│   └── assets/
│       └── hero.png          # 测试图片
├── backend/
│   ├── app.py                # Flask 主应用
│   ├── mmx_vision_mcp.py     # MiniMax MCP 封装器
│   └── requirements.txt
├── package.json
└── vite.config.ts
```

## 主要功能实现

### 流式对话
- 端点: `/api/chat/stream`
- 使用 Server-Sent Events (SSE)
- 支持 AbortSignal 取消请求
- 对话历史存储在后端内存中

### 多对话管理
- 存储位置: localStorage (`minimax-vision-conversations-{deviceId}`)
- 设备隔离: 每浏览器独立存储
- 支持创建、切换、删除对话

### Markdown 渲染
- 使用 `marked` 库
- 使用 `DOMPurify` 防止 XSS
- 支持代码块、表格、列表等

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| MINIMAX_API_KEY | ✅ | - | MiniMax API Key |
| CHAT_API_KEY | ✅ | - | 天行AI 对话 API Key |
| CHAT_API_HOST | ❌ | https://ai.1i.wiki/v1 | 对话 API 地址 |
| API_KEY | ❌ | - | 外部 API 密钥 |
| DEBUG | ❌ | false | 调试模式 |

## 更新日志

### v0.2.0 (2026-05-05)
- ✅ 流式对话输出 (SSE)
- ✅ 停止按钮功能 (AbortSignal)
- ✅ 多对话历史管理
- ✅ 设备隔离存储
- ✅ Markdown 渲染增强
- ✅ 全屏对话模式
- ✅ 图片粘贴上传

### v0.1.0 (2026-05-04)
- 初始版本
- 图片分析基础功能
- URL/Base64 图片支持

## License

MIT
