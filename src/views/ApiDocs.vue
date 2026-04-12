<template>
  <div class="api-docs">
    <header class="docs-header">
      <div class="header-content">
        <h1>📚 MiniMax Vision API 文档</h1>
        <p>版本 2.0.0 - 图片理解 API 服务</p>
        <div class="base-url">
          <span class="label">Base URL:</span>
          <code>{{ baseUrl }}/api</code>
        </div>
      </div>
      <a href="/" class="back-btn">← 返回首页</a>
    </header>

    <main class="docs-content">
      <!-- 认证部分 -->
      <section class="docs-section">
        <h2>🔐 认证</h2>
        <div class="auth-box">
          <p>API 使用 <code>X-API-Key</code> 请求头进行认证：</p>
          <pre><code>curl -H "X-API-Key: your-api-key" -X POST {{ baseUrl }}/api/analyze ...</code></pre>
          <p class="note">💡 如果未设置 <code>API_KEY</code> 环境变量，则无需认证（不推荐用于生产环境）</p>
        </div>
      </section>

      <!-- 端点列表 -->
      <section class="docs-section">
        <h2>📡 端点</h2>
        
        <!-- /api/analyze -->
        <div class="endpoint-card">
          <div class="endpoint-header">
            <span class="method post">POST</span>
            <code class="path">/api/analyze</code>
            <span class="tag">上传文件</span>
          </div>
          <p class="description">上传图片文件进行分析</p>
          
          <div class="endpoint-details">
            <h4>Content-Type</h4>
            <code>multipart/form-data</code>
            
            <h4>参数</h4>
            <table class="params-table">
              <thead>
                <tr>
                  <th>参数</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>image</code></td>
                  <td>File</td>
                  <td><span class="required">✅</span></td>
                  <td>图片文件</td>
                </tr>
                <tr>
                  <td><code>prompt</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>分析提示词（默认中文详细描述）</td>
                </tr>
                <tr>
                  <td><code>format</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>返回格式：<code>json</code>（默认）或 <code>text</code></td>
                </tr>
              </tbody>
            </table>
            
            <h4>示例</h4>
            <pre><code>curl -X POST {{ baseUrl }}/api/analyze \
  -H "X-API-Key: your-key" \
  -F "image=@photo.jpg" \
  -F "prompt=请描述这张图片"</code></pre>
          </div>
        </div>

        <!-- /api/analyze/base64 -->
        <div class="endpoint-card">
          <div class="endpoint-header">
            <span class="method post">POST</span>
            <code class="path">/api/analyze/base64</code>
            <span class="tag">Base64</span>
          </div>
          <p class="description">发送 Base64 编码的图片进行分析</p>
          
          <div class="endpoint-details">
            <h4>Content-Type</h4>
            <code>application/json</code>
            
            <h4>请求体</h4>
            <pre><code>{
  "image": "data:image/jpeg;base64,/9j/4AAQ...",  // 或纯 base64
  "prompt": "请详细描述",
  "format": "json"
}</code></pre>
            
            <h4>参数</h4>
            <table class="params-table">
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>image</code></td>
                  <td>string</td>
                  <td><span class="required">✅</span></td>
                  <td>Base64 图片数据（支持 data URI 或纯 base64）</td>
                </tr>
                <tr>
                  <td><code>prompt</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>分析提示词</td>
                </tr>
                <tr>
                  <td><code>format</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>返回格式：<code>json</code> 或 <code>text</code></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- /api/analyze/url -->
        <div class="endpoint-card">
          <div class="endpoint-header">
            <span class="method post">POST</span>
            <code class="path">/api/analyze/url</code>
            <span class="tag">URL</span>
          </div>
          <p class="description">通过图片 URL 进行分析</p>
          
          <div class="endpoint-details">
            <h4>Content-Type</h4>
            <code>application/json</code>
            
            <h4>请求体</h4>
            <pre><code>{
  "url": "https://example.com/photo.jpg",
  "prompt": "这张图片里有什么？"
}</code></pre>
            
            <h4>参数</h4>
            <table class="params-table">
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>url</code></td>
                  <td>string</td>
                  <td><span class="required">✅</span></td>
                  <td>图片 URL（支持 HTTP/HTTPS）</td>
                </tr>
                <tr>
                  <td><code>prompt</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>分析提示词</td>
                </tr>
                <tr>
                  <td><code>format</code></td>
                  <td>string</td>
                  <td><span class="optional">❌</span></td>
                  <td>返回格式：<code>json</code> 或 <code>text</code></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- /api/health -->
        <div class="endpoint-card">
          <div class="endpoint-header">
            <span class="method get">GET</span>
            <code class="path">/api/health</code>
            <span class="tag">健康检查</span>
          </div>
          <p class="description">检查 API 服务状态</p>
        </div>
      </section>

      <!-- 响应格式 -->
      <section class="docs-section">
        <h2>📋 响应格式</h2>
        
        <h3>JSON 响应（默认）</h3>
        <pre><code>{
  "success": true,
  "result": "这是一张街道照片，阳光明媚...",
  "metadata": {
    "filename": "photo.jpg",
    "size": 123456,
    "prompt": "请描述这张图片",
    "model": "MiniMax-MCP"
  }
}</code></pre>
        
        <h3>Text 响应</h3>
        <p>当 <code>format=text</code> 时，直接返回纯文本</p>
      </section>

      <!-- 错误码 -->
      <section class="docs-section">
        <h2>⚠️ 错误码</h2>
        <table class="error-table">
          <thead>
            <tr>
              <th>code</th>
              <th>说明</th>
              <th>HTTP 状态码</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>MISSING_API_KEY</code></td>
              <td>未提供 API 密钥</td>
              <td>401</td>
            </tr>
            <tr>
              <td><code>INVALID_API_KEY</code></td>
              <td>API 密钥无效</td>
              <td>403</td>
            </tr>
            <tr>
              <td><code>RATE_LIMITED</code></td>
              <td>请求过于频繁（60次/分钟/IP）</td>
              <td>429</td>
            </tr>
            <tr>
              <td><code>MISSING_IMAGE</code></td>
              <td>未提供图片</td>
              <td>400</td>
            </tr>
            <tr>
              <td><code>INVALID_IMAGE</code></td>
              <td>图片格式无效或太大（最大 10MB）</td>
              <td>400/413</td>
            </tr>
            <tr>
              <td><code>ANALYSIS_ERROR</code></td>
              <td>分析失败</td>
              <td>500</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 示例代码 -->
      <section class="docs-section">
        <h2>💻 代码示例</h2>
        
        <div class="code-tabs">
          <button 
            :class="{ active: activeTab === 'python' }" 
            @click="activeTab = 'python'"
          >Python</button>
          <button 
            :class="{ active: activeTab === 'javascript' }" 
            @click="activeTab = 'javascript'"
          >JavaScript</button>
          <button 
            :class="{ active: activeTab === 'curl' }" 
            @click="activeTab = 'curl'"
          >cURL</button>
        </div>

        <div v-if="activeTab === 'python'" class="code-block">
          <pre><code>import requests

url = "{{ baseUrl }}/api/analyze"
headers = {"X-API-Key": "your-key"}

# 上传文件方式
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
    "{{ baseUrl }}/api/analyze/base64",
    json={"image": b64, "prompt": "请描述"},
    headers={**headers, "Content-Type": "application/json"}
)
print(resp.json())

# URL 方式
resp = requests.post(
    "{{ baseUrl }}/api/analyze/url",
    json={"url": "https://example.com/photo.jpg", "prompt": "这张图片里有什么？"},
    headers={**headers, "Content-Type": "application/json"}
)
print(resp.json())</code></pre>
        </div>

        <div v-if="activeTab === 'javascript'" class="code-block">
          <pre><code>// 上传文件方式
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('prompt', '请描述这张图片');

const resp = await fetch('{{ baseUrl }}/api/analyze', {
  method: 'POST',
  headers: { 'X-API-Key': 'your-key' },
  body: formData
});
const data = await resp.json();
console.log(data.result);

// Base64 方式
const resp = await fetch('{{ baseUrl }}/api/analyze/base64', {
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
const data = await resp.json();
console.log(data.result);

// URL 方式
const resp = await fetch('{{ baseUrl }}/api/analyze/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-key'
  },
  body: JSON.stringify({
    url: 'https://example.com/photo.jpg',
    prompt: '这张图片里有什么？'
  })
});
const data = await resp.json();
console.log(data.result);</code></pre>
        </div>

        <div v-if="activeTab === 'curl'" class="code-block">
          <pre><code># 上传文件
curl -X POST {{ baseUrl }}/api/analyze \
  -H "X-API-Key: your-key" \
  -F "image=@photo.jpg" \
  -F "prompt=请描述这张图片"

# Base64
curl -X POST {{ baseUrl }}/api/analyze/base64 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"image": "base64...", "prompt": "请描述"}'

# URL
curl -X POST {{ baseUrl }}/api/analyze/url \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"url": "https://example.com/photo.jpg", "prompt": "请描述"}'

# 健康检查
curl {{ baseUrl }}/api/health</code></pre>
        </div>
      </section>
    </main>

    <footer class="docs-footer">
      <p>Powered by MiniMax Vision API + Vue 3</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const activeTab = ref<'python' | 'javascript' | 'curl'>('python')

const baseUrl = computed(() => {
  return window.location.origin.replace(':5173', ':5001')
})
</script>

<style scoped>
.api-docs {
  min-height: 100vh;
  background: #f5f7fa;
}

.docs-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content h1 {
  margin: 0;
  font-size: 1.8rem;
}

.header-content p {
  margin: 0.5rem 0 1rem;
  opacity: 0.9;
}

.base-url {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.base-url code {
  background: rgba(0, 0, 0, 0.2);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.back-btn {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.docs-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.docs-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.docs-section h2 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1.3rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #667eea;
}

.docs-section h3 {
  margin: 1rem 0 0.5rem;
  color: #555;
  font-size: 1rem;
}

.docs-section h4 {
  margin: 1rem 0 0.5rem;
  color: #666;
  font-size: 0.95rem;
}

.auth-box {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.auth-box p {
  margin: 0 0 0.5rem;
}

.note {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.5;
}

code {
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #d63384;
}

.endpoint-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.endpoint-card:last-child {
  margin-bottom: 0;
}

.endpoint-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.method {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
}

.method.post {
  background: #49cc90;
}

.method.get {
  background: #61affe;
}

.path {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #333;
}

.tag {
  background: #667eea;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.description {
  color: #666;
  margin: 0 0 1rem;
}

.endpoint-details h4 {
  margin: 1rem 0 0.5rem;
  color: #555;
}

.params-table,
.error-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.params-table th,
.params-table td,
.error-table th,
.error-table td {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.params-table th {
  background: #f8f9fa;
  font-weight: 600;
}

.error-table {
  background: #f8f9fa;
  border-radius: 8px;
}

.required {
  color: #dc3545;
}

.optional {
  color: #28a745;
}

.code-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.code-tabs button {
  padding: 0.5rem 1rem;
  border: none;
  background: #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.code-tabs button.active {
  background: #667eea;
  color: white;
}

.code-tabs button:hover:not(.active) {
  background: #dee2e6;
}

.code-block pre {
  margin: 0;
}

.docs-footer {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>
