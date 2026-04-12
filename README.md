# MiniMax Vision API

基于 Vue 3 + MiniMax MCP 的图片理解 API 服务，支持第三方系统调用。

## 功能

- 📷 图片上传分析（multipart/form-data）
- 🔗 URL 图片分析（远程图片链接）
- 📊 Base64 图片分析（JSON API）
- 🔒 API 密钥认证
- ⏱️ 请求限流保护
- 📝 详细的 API 文档

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

# 外部 API 密钥（可选，用于保护 API）
export API_KEY="your-api-key-for-clients"

# 调试模式
export DEBUG=false
```

### 3. 启动服务

```bash
cd backend
python app.py
```

- API 服务: http://localhost:5001
- 健康检查: http://localhost:5001/api/health
- API 文档: http://localhost:5001/api/docs

### 4. 启动前端（可选）

```bash
npm run dev
```

前端运行在 http://localhost:5173

## API 文档

完整的 API 文档在 `/api/docs` 端点。

### 认证

API 使用 `X-API-Key` 请求头认证：

```bash
curl -H "X-API-Key: your-api-key" ...
```

如果不设置 `API_KEY` 环境变量，则无需认证。

### 端点

#### POST /api/analyze

上传图片文件进行分析

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "X-API-Key: your-key" \
  -F "image=@photo.jpg" \
  -F "prompt=请描述这张图片"
```

**参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | ✅ | 图片文件 |
| prompt | string | ❌ | 分析提示词（默认中文详细描述）|
| format | string | ❌ | 返回格式：`json`（默认）或 `text` |

**响应**:
```json
{
  "success": true,
  "result": "这是一张街道照片，阳光明媚...",
  "metadata": {
    "filename": "photo.jpg",
    "size": 123456,
    "prompt": "请描述这张图片",
    "model": "MiniMax-MCP"
  }
}
```

#### POST /api/analyze/base64

发送 Base64 编码的图片

```bash
curl -X POST http://localhost:5001/api/analyze/base64 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "prompt": "请详细描述"
  }'
```

**参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | string | ✅ | Base64 图片数据（支持 data URI 或纯 base64）|
| prompt | string | ❌ | 分析提示词 |
| format | string | ❌ | 返回格式：`json` 或 `text` |

#### POST /api/analyze/url

通过 URL 分析远程图片

```bash
curl -X POST http://localhost:5001/api/analyze/url \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "url": "https://example.com/photo.jpg",
    "prompt": "这张图片里有什么？"
  }'
```

**参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | ✅ | 图片 URL |
| prompt | string | ❌ | 分析提示词 |
| format | string | ❌ | 返回格式：`json` 或 `text` |

### 错误码

| code | 说明 |
|------|------|
| MISSING_API_KEY | 未提供 API 密钥 |
| INVALID_API_KEY | API 密钥无效 |
| RATE_LIMITED | 请求过于频繁（60次/分钟）|
| MISSING_IMAGE | 未提供图片 |
| INVALID_IMAGE | 图片格式无效或太大 |
| ANALYSIS_ERROR | 分析失败 |

### 示例代码

**Python 调用示例**:

```python
import requests

url = "http://localhost:5001/api/analyze"
headers = {"X-API-Key": "your-key"}

# 上传文件
with open("photo.jpg", "rb") as f:
    files = {"image": f}
    data = {"prompt": "请描述这张图片"}
    resp = requests.post(url, files=files, data=data, headers=headers)
    print(resp.json())

# Base64 方式
import base64
with open("photo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
resp = requests.post(
    "http://localhost:5001/api/analyze/base64",
    json={"image": b64, "prompt": "请描述"},
    headers={**headers, "Content-Type": "application/json"}
)
print(resp.json())
```

**JavaScript 调用示例**:

```javascript
// 上传文件
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('prompt', '请描述这张图片');

const resp = await fetch('http://localhost:5001/api/analyze', {
  method: 'POST',
  headers: { 'X-API-Key': 'your-key' },
  body: formData
});
console.log(await resp.json());

// Base64
const resp = await fetch('http://localhost:5001/api/analyze/base64', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-key'
  },
  body: JSON.stringify({
    image: base64String,
    prompt: '请描述这张图片'
  })
});
console.log(await resp.json());
```

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Pinia
- **后端**: Python Flask + MiniMax MCP Tools
- **限流**: 60 请求/分钟/IP

## 项目结构

```
minimax-vision-frontend/
├── src/
│   ├── api/analysis.ts       # 前端 API 调用
│   ├── components/
│   │   ├── ImageUploader.vue  # 图片上传
│   │   └── AnalysisResult.vue # 结果展示
│   └── views/Home.vue         # 主页
├── backend/
│   ├── app.py                # Flask API 服务
│   └── requirements.txt
└── package.json
```

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| MINIMAX_API_KEY | ✅ | - | MiniMax API Key |
| API_KEY | ❌ | - | 外部 API 密钥（不设置则开放访问）|
| API_KEY | ❌ | false | 调试模式 |
| MINIMAX_API_HOST | ❌ | https://api.minimaxi.com | MiniMax API 端点 |

## License

MIT
