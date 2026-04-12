# MiniMax Vision Frontend

基于 Vue 3 + MiniMax MCP 图片理解工具的前端应用

## 功能

- 📷 图片上传（支持拖拽）
- 🤖 AI 智能图片分析
- 📝 返回详细的中文分析结果

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Pinia
- **后端**: Python Flask + MiniMax MCP Tools
- **API**: RESTful API

## 项目结构

```
minimax-vision-frontend/
├── src/
│   ├── api/
│   │   └── analysis.ts      # API 调用
│   ├── components/
│   │   ├── ImageUploader.vue  # 图片上传组件
│   │   └── AnalysisResult.vue # 分析结果展示
│   ├── views/
│   │   └── Home.vue          # 主页
│   ├── router/
│   │   └── index.ts         # 路由配置
│   ├── App.vue
│   └── main.ts
├── backend/
│   ├── app.py               # Flask 后端服务
│   └── requirements.txt
└── package.json
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
# 设置 MiniMax API Key
export MINIMAX_API_KEY="your_api_key_here"
```

### 3. 启动后端服务

```bash
cd backend
python app.py
```

后端服务运行在 http://localhost:5000

### 4. 启动前端开发服务器

```bash
npm run dev
```

前端运行在 http://localhost:5173

## API 接口

### POST /analyze

上传图片并获取分析结果

**请求**:
- Content-Type: `multipart/form-data`
- 参数:
  - `image`: 图片文件
  - `prompt`: (可选) 分析提示词

**响应**:
```json
{
  "success": true,
  "result": "图片分析结果..."
}
```

### GET /health

健康检查接口

## MiniMax MCP 工具

本项目使用 MiniMax 官方的 `understand_image` MCP 工具进行图片理解。

### 工作原理

1. 前端上传图片到 Flask 后端
2. 后端调用 `minimax-coding-plan-mcp` (via uvx)
3. MCP 服务器通过 JSON-RPC 与 MiniMax API 交互
4. 返回分析结果

### 所需环境

- `MINIMAX_API_KEY`: MiniMax Token Plan API Key
- `MINIMAX_API_HOST`: API 端点 (默认: https://api.minimaxi.com)

## 开发说明

### 前端开发

```bash
npm run dev     # 开发模式
npm run build   # 生产构建
```

### 后端开发

```bash
cd backend
python app.py   # 开发模式 (debug=True)
```

## License

MIT
