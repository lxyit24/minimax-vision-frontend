<template>
  <div class="docs-page">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">🔮</span>
        <span class="brand-name">MiniMax Vision</span>
        <span class="brand-badge">API v2.0</span>
      </div>
      <div class="nav-links">
        <a href="/" class="nav-link">← 返回首页</a>
      </div>
    </header>

    <div class="docs-layout">
      <!-- 侧边栏导航 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <a 
            v-for="section in sections" 
            :key="section.id"
            :href="'#' + section.id"
            :class="['sidebar-link', { active: activeSection === section.id }]"
            @click.prevent="scrollToSection(section.id)"
          >
            {{ section.icon }} {{ section.title }}
          </a>
        </nav>
        
        <div class="sidebar-footer">
          <div class="rate-limit-box">
            <span class="rate-label">Rate Limit</span>
            <span class="rate-value">60 req/min</span>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- Hero Section -->
        <section class="hero-section" id="overview">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            REST API
          </div>
          <h1>强大的图片理解 API</h1>
          <p class="hero-desc">
            集成 MiniMax 最先进的视觉理解模型，只需几行代码即可为你的应用添加图片分析能力。支持文件上传、Base64 和 URL 多种方式。
          </p>
          <div class="hero-actions">
            <a href="#authentication" class="btn btn-primary">开始使用 →</a>
            <a href="#endpoints" class="btn btn-secondary">查看文档</a>
          </div>
          <div class="hero-stats">
            <div class="stat">
              <span class="stat-value">3</span>
              <span class="stat-label">端点</span>
            </div>
            <div class="stat">
              <span class="stat-value">60/min</span>
              <span class="stat-label">速率限制</span>
            </div>
            <div class="stat">
              <span class="stat-value">10MB</span>
              <span class="stat-label">最大图片</span>
            </div>
          </div>
        </section>

        <!-- 快速开始 -->
        <section class="doc-section" id="authentication">
          <div class="section-header">
            <div class="section-icon">🔐</div>
            <div>
              <h2>认证</h2>
              <p class="section-desc">所有 API 请求都需要通过 X-API-Key Header 进行认证</p>
            </div>
          </div>
          
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">cURL</span>
              <button class="copy-btn" @click="copyCode(authCode)">复制</button>
            </div>
            <pre><code>{{ authCode }}</code></pre>
          </div>

          <div class="info-cards">
            <div class="info-card info">
              <span class="info-icon">💡</span>
              <div>
                <strong>获取 API Key</strong>
                <p>API Key 通过环境变量 <code>API_KEY</code> 配置，未设置则无需认证（仅开发环境）</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 端点列表 -->
        <section class="doc-section" id="endpoints">
          <div class="section-header">
            <div class="section-icon">📡</div>
            <div>
              <h2>API 端点</h2>
              <p class="section-desc">三个核心端点，满足不同的图片分析场景</p>
            </div>
          </div>

          <!-- 端点卡片 -->
          <div 
            v-for="endpoint in endpoints" 
            :key="endpoint.path"
            class="endpoint-card"
            :id="endpoint.id"
          >
            <div class="endpoint-meta">
              <span :class="['method-badge', endpoint.method.toLowerCase()]">{{ endpoint.method }}</span>
              <code class="endpoint-path">{{ endpoint.path }}</code>
              <span class="endpoint-tag">{{ endpoint.tag }}</span>
            </div>
            <p class="endpoint-desc">{{ endpoint.description }}</p>
            
            <!-- 参数表格 -->
            <div class="params-table-wrapper">
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
                  <tr v-for="param in endpoint.params" :key="param.name">
                    <td><code class="param-name">{{ param.name }}</code></td>
                    <td><span class="param-type">{{ param.type }}</span></td>
                    <td>
                      <span :class="['required-badge', param.required ? 'yes' : 'no']">
                        {{ param.required ? '✓' : '—' }}
                      </span>
                    </td>
                    <td class="param-desc">{{ param.desc }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 示例代码 -->
            <div class="code-tabs">
              <button 
                v-for="tab in ['cURL', 'Python', 'JavaScript']"
                :key="tab"
                :class="['tab-btn', { active: activeCodeTab[endpoint.path] === tab.toLowerCase() }]"
                @click="activeCodeTab[endpoint.path] = tab.toLowerCase()"
              >
                {{ tab }}
              </button>
            </div>
            <div class="code-block small">
              <pre><code>{{ getEndpointCode(endpoint, activeCodeTab[endpoint.path]) }}</code></pre>
            </div>
          </div>
        </section>

        <!-- 响应格式 -->
        <section class="doc-section" id="response">
          <div class="section-header">
            <div class="section-icon">📋</div>
            <div>
              <h2>响应格式</h2>
              <p class="section-desc">API 默认返回 JSON 格式，支持 text 纯文本响应</p>
            </div>
          </div>

          <div class="response-examples">
            <div class="response-card">
              <div class="response-header">
                <span class="response-label">JSON 响应</span>
                <span class="response-default">默认</span>
              </div>
              <pre><code>{{ jsonResponse }}</code></pre>
            </div>
            
            <div class="response-card">
              <div class="response-header">
                <span class="response-label">Text 响应</span>
                <span class="response-tag">format=text</span>
              </div>
              <pre><code>{{ textResponse }}</code></pre>
            </div>
          </div>
        </section>

        <!-- 错误码 -->
        <section class="doc-section" id="errors">
          <div class="section-header">
            <div class="section-icon">⚠️</div>
            <div>
              <h2>错误处理</h2>
              <p class="section-desc">API 使用标准 HTTP 状态码和业务错误码</p>
            </div>
          </div>

          <div class="error-grid">
            <div 
              v-for="error in errors" 
              :key="error.code"
              class="error-card"
            >
              <div class="error-header">
                <span :class="['error-code', error.level]">{{ error.code }}</span>
                <span class="error-status">HTTP {{ error.status }}</span>
              </div>
              <p class="error-desc">{{ error.desc }}</p>
            </div>
          </div>
        </section>

        <!-- 底部CTA -->
        <section class="cta-section">
          <div class="cta-content">
            <h2>准备好开始了吗？</h2>
            <p>立即为你的应用添加图片理解能力</p>
            <a href="/" class="btn btn-primary btn-large">← 返回首页试用</a>
          </div>
        </section>
      </main>
    </div>

    <!-- Toast 提示 -->
    <Transition name="toast">
      <div v-if="showToast" class="toast">
        ✓ {{ toastMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'

const activeSection = ref('overview')
const showToast = ref(false)
const toastMessage = ref('')

const authCode = `curl -X POST http://127.0.0.1:5001/api/analyze \\
  -H "X-API-Key: your-api-key" \\
  -F "image=@photo.jpg" \\
  -F "prompt=请描述这张图片"`

const sections = [
  { id: 'overview', title: '概述', icon: '🚀' },
  { id: 'authentication', title: '认证', icon: '🔐' },
  { id: 'endpoints', title: '端点', icon: '📡' },
  { id: 'response', title: '响应格式', icon: '📋' },
  { id: 'errors', title: '错误处理', icon: '⚠️' },
]

const endpoints = [
  {
    id: 'upload',
    method: 'POST',
    path: '/api/analyze',
    tag: '文件上传',
    description: '通过 multipart/form-data 上传图片文件进行分析，适合前端直接调用',
    contentType: 'multipart/form-data',
    params: [
      { name: 'image', type: 'File', required: true, desc: '图片文件（支持 JPG/PNG/GIF/WebP，最大 10MB）' },
      { name: 'prompt', type: 'string', required: false, desc: '分析提示词，不填则使用默认中文详细描述' },
      { name: 'format', type: 'string', required: false, desc: '返回格式：json（默认）或 text' },
    ]
  },
  {
    id: 'base64',
    method: 'POST',
    path: '/api/analyze/base64',
    tag: 'Base64',
    description: '发送 Base64 编码的图片数据进行高效传输，适合后端服务集成',
    contentType: 'application/json',
    params: [
      { name: 'image', type: 'string', required: true, desc: 'Base64 字符串（支持 data URI 或纯 base64）' },
      { name: 'prompt', type: 'string', required: false, desc: '分析提示词' },
      { name: 'format', type: 'string', required: false, desc: '返回格式：json 或 text' },
    ]
  },
  {
    id: 'url',
    method: 'POST',
    path: '/api/analyze/url',
    tag: 'URL',
    description: '直接通过图片 URL 进行分析，无需上传文件，适合公开图片链接',
    contentType: 'application/json',
    params: [
      { name: 'url', type: 'string', required: true, desc: '图片 URL（支持 HTTP/HTTPS，必须可公开访问）' },
      { name: 'prompt', type: 'string', required: false, desc: '分析提示词' },
      { name: 'format', type: 'string', required: false, desc: '返回格式：json 或 text' },
    ]
  },
]

const activeCodeTab = reactive<Record<string, string>>({
  '/api/analyze': 'curl',
  '/api/analyze/base64': 'curl',
  '/api/analyze/url': 'curl',
})

const errors = [
  { code: 'MISSING_API_KEY', status: '401', level: 'error', desc: '未提供 API 密钥' },
  { code: 'INVALID_API_KEY', status: '403', level: 'error', desc: 'API 密钥无效' },
  { code: 'RATE_LIMITED', status: '429', level: 'warning', desc: '请求过于频繁（60次/分钟/IP）' },
  { code: 'MISSING_IMAGE', status: '400', level: 'error', desc: '未提供图片数据' },
  { code: 'INVALID_IMAGE', status: '400', level: 'error', desc: '图片格式无效或文件损坏' },
  { code: 'ANALYSIS_ERROR', status: '500', level: 'error', desc: '图片分析失败，请稍后重试' },
]

const jsonResponse = `{
  "success": true,
  "result": "这是一张城市街道的照片，阳光明媚...",
  "metadata": {
    "filename": "photo.jpg",
    "size": 123456,
    "prompt": "请描述这张图片",
    "model": "MiniMax-MCP"
  }
}`

const textResponse = `这是一张城市街道的照片，阳光明媚，街道两旁种满了银杏树...`

function getEndpointCode(endpoint: any, tab: string): string {
  const base = 'http://127.0.0.1:5001'
  if (endpoint.path === '/api/analyze') {
    if (tab === 'curl') return `curl -X POST ${base}/api/analyze \\
  -H "X-API-Key: your-key" \\
  -F "image=@photo.jpg" \\
  -F "prompt=请描述这张图片"`
    if (tab === 'python') return `import requests

files = {'image': open('photo.jpg', 'rb')}
data = {'prompt': '请描述这张图片'}
resp = requests.post(
    '${base}/api/analyze',
    files=files, data=data,
    headers={'X-API-Key': 'your-key'}
)
print(resp.json())`
    return `const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('prompt', '请描述这张图片');

const resp = await fetch('${base}/api/analyze', {
  method: 'POST',
  headers: { 'X-API-Key': 'your-key' },
  body: formData
});
const data = await resp.json();`
  }
  
  if (endpoint.path === '/api/analyze/base64') {
    if (tab === 'curl') return `curl -X POST ${base}/api/analyze/base64 \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key" \\
  -d '{"image": "base64...", "prompt": "请描述"}'`
    if (tab === 'python') return `import base64, requests

with open('photo.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

resp = requests.post(
    '${base}/api/analyze/base64',
    json={'image': b64, 'prompt': '请描述'},
    headers={'X-API-Key': 'your-key'}
)
print(resp.json())`
    return `const b64 = await fetchAsBase64(fileInput.files[0]);

const resp = await fetch('${base}/api/analyze/base64', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-key'
  },
  body: JSON.stringify({ image: b64, prompt: '请描述' })
});`
  }
  
  if (tab === 'curl') return `curl -X POST ${base}/api/analyze/url \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key" \\
  -d '{"url": "https://example.com/photo.jpg", "prompt": "描述"}'`
  if (tab === 'python') return `import requests

resp = requests.post(
    '${base}/api/analyze/url',
    json={'url': 'https://example.com/photo.jpg', 'prompt': '描述'},
    headers={'Content-Type': 'application/json', 'X-API-Key': 'your-key'}
)
print(resp.json())`
  return `const resp = await fetch('${base}/api/analyze/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-key'
  },
  body: JSON.stringify({
    url: 'https://example.com/photo.jpg',
    prompt: '描述'
  })
});`
}

function scrollToSection(id: string) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeSection.value = id
  }
}

function handleScroll() {
  const scrollY = window.scrollY
  for (const section of sections) {
    const el = document.getElementById(section.id)
    if (el && el.offsetTop <= scrollY + 100) {
      activeSection.value = section.id
    }
  }
}

function copyCode(code: string) {
  navigator.clipboard.writeText(code)
  showToastMessage('已复制到剪贴板')
}

function showToastMessage(msg: string) {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 2000)
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* ===== 基础变量 ===== */
.docs-page {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #818cf8;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --bg-code: #0d1117;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: #334155;
}

/* ===== 顶部导航 ===== */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 2rem;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.brand-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.brand-badge {
  background: var(--primary);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--text-primary);
}

/* ===== 布局 ===== */
.docs-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: calc(100vh - 60px);
}

/* ===== 侧边栏 ===== */
.sidebar {
  position: sticky;
  top: 60px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 1.5rem;
  border-right: 1px solid var(--border);
  background: var(--bg-dark);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-link {
  display: block;
  padding: 0.6rem 0.75rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.sidebar-link:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

.sidebar-link.active {
  background: var(--primary);
  color: white;
}

.sidebar-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.rate-limit-box {
  background: var(--bg-card);
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rate-label {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.rate-value {
  color: var(--success);
  font-weight: 600;
  font-size: 0.85rem;
}

/* ===== 主内容 ===== */
.main-content {
  padding: 2rem 3rem;
  max-width: 900px;
}

/* ===== Hero Section ===== */
.hero-section {
  padding: 3rem 0 4rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-light);
  padding: 0.4rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--primary-light);
  border-radius: 50%;
}

.hero-section h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 1rem;
  line-height: 1.2;
}

.hero-desc {
  color: var(--text-secondary);
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0 0 1.5rem;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--border);
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1rem;
}

.hero-stats {
  display: flex;
  gap: 2.5rem;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ===== Doc Section ===== */
.doc-section {
  padding: 2.5rem 0;
  border-bottom: 1px solid var(--border);
}

.doc-section:last-of-type {
  border-bottom: none;
}

.section-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border-radius: 10px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--text-primary);
}

.section-desc {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* ===== Code Block ===== */
.code-block {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem 0;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--border);
}

.code-lang {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.copy-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: var(--border);
  color: var(--text-primary);
}

.code-block pre {
  margin: 0;
  padding: 1rem;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.85rem;
  color: #e2e8f0;
  background: transparent;
  padding: 0;
}

.code-block.small pre {
  padding: 0.75rem 1rem;
}

.code-block.small code {
  font-size: 0.8rem;
}

/* ===== Code Tabs ===== */
.code-tabs {
  display: flex;
  gap: 0.25rem;
  margin: 1rem 0 0;
}

.tab-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.4rem 0.75rem;
  border-radius: 6px 6px 0 0;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: var(--bg-code);
  color: var(--text-primary);
  border-bottom-color: var(--bg-code);
}

.tab-btn:hover:not(.active) {
  color: var(--text-primary);
}

/* ===== Info Cards ===== */
.info-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.info-card {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.info-card.info .info-icon {
  font-size: 1.1rem;
}

.info-card strong {
  display: block;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.info-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.info-card code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 0.8rem;
}

/* ===== Endpoint Card ===== */
.endpoint-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.endpoint-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.method-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.method-badge.post {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.method-badge.get {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.endpoint-path {
  background: rgba(0, 0, 0, 0.3);
  color: var(--text-primary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.endpoint-tag {
  background: var(--primary);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.endpoint-desc {
  color: var(--text-secondary);
  margin: 0 0 1rem;
  font-size: 0.9rem;
}

/* ===== Params Table ===== */
.params-table-wrapper {
  overflow-x: auto;
  margin: 1rem 0;
}

.params-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.params-table th {
  text-align: left;
  padding: 0.6rem 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.params-table td {
  padding: 0.6rem 0.75rem;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
}

.param-name {
  color: #f472b6;
  background: transparent;
}

.param-type {
  color: #38bdf8;
  font-size: 0.8rem;
}

.required-badge {
  font-weight: 600;
}

.required-badge.yes {
  color: var(--success);
}

.required-badge.no {
  color: var(--text-muted);
}

.param-desc {
  color: var(--text-secondary);
}

/* ===== Response Examples ===== */
.response-examples {
  display: grid;
  gap: 1rem;
}

.response-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid var(--border);
}

.response-label {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.response-default {
  background: var(--success);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.response-tag {
  background: var(--bg-code);
  color: var(--text-muted);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  border: 1px solid var(--border);
}

.response-card pre {
  margin: 0;
  padding: 1rem;
}

.response-card code {
  font-family: 'Fira Code', monospace;
  font-size: 0.8rem;
  color: #a5b4fc;
  background: transparent;
  padding: 0;
}

/* ===== Error Grid ===== */
.error-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.error-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.error-code {
  font-family: monospace;
  font-size: 0.85rem;
  font-weight: 600;
}

.error-code.error {
  color: var(--error);
}

.error-code.warning {
  color: var(--warning);
}

.error-status {
  color: var(--text-muted);
  font-size: 0.75rem;
  background: var(--bg-code);
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
}

.error-desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* ===== CTA Section ===== */
.cta-section {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: 16px;
  padding: 3rem;
  margin: 3rem 0;
  text-align: center;
}

.cta-content h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: white;
}

.cta-content p {
  margin: 0 0 1.5rem;
  color: rgba(255, 255, 255, 0.8);
}

/* ===== Toast ===== */
.toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--success);
  font-size: 0.9rem;
  z-index: 1000;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .docs-layout {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    display: none;
  }
  
  .main-content {
    padding: 1.5rem;
  }
  
  .hero-section h1 {
    font-size: 1.8rem;
  }
  
  .hero-stats {
    flex-wrap: wrap;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 1.25rem 0.75rem;
  }
  
  .hero-section h1 {
    font-size: 1.2rem;
  }
  
  .hero-section p {
    font-size: 0.85rem;
  }
  
  .hero-stats {
    justify-content: center;
  }
  
  .stat-item {
    padding: 0.4rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .main-content {
    padding: 0.75rem 0.5rem 4rem;
  }
  
  .section-title {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }
  
  .endpoint-card {
    padding: 0.75rem;
    margin-bottom: 0.65rem;
    border-radius: 8px;
  }
  
  .method {
    padding: 0.2rem 0.4rem;
    font-size: 0.65rem;
    border-radius: 3px;
  }
  
  .endpoint-path {
    font-size: 0.85rem;
    word-break: break-all;
  }
  
  .endpoint-desc {
    font-size: 0.8rem;
    margin-top: 0.35rem;
  }
  
  .code-block {
    border-radius: 6px;
    margin-top: 0.5rem;
  }
  
  .code-header {
    padding: 0.4rem 0.6rem;
    font-size: 0.7rem;
    border-radius: 6px 6px 0 0;
  }
  
  .code-block pre {
    padding: 0.6rem;
    font-size: 0.75rem;
    border-radius: 0 0 6px 6px;
    overflow-x: auto;
  }
  
  .copy-btn {
    padding: 0.25rem 0.4rem;
    font-size: 0.65rem;
  }
  
  .tab-btn {
    padding: 0.4rem 0.6rem;
    font-size: 0.75rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .feature-card {
    padding: 0.75rem;
  }
  
  .auth-note {
    padding: 0.6rem 0.75rem;
    font-size: 0.8rem;
    border-radius: 6px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 1rem 0.5rem;
  }
  
  .hero-section h1 {
    font-size: 1.1rem;
  }
  
  .hero-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  .hero-stats {
    gap: 0.5rem;
  }
  
  .stat-item {
    padding: 0.35rem 0.6rem;
    font-size: 0.7rem;
  }
  
  .main-content {
    padding: 0.5rem 0.35rem 4rem;
  }
  
  .section-title {
    font-size: 0.9rem;
  }
  
  .endpoint-card {
    padding: 0.6rem;
    margin-bottom: 0.5rem;
  }
  
  .method {
    font-size: 0.6rem;
    padding: 0.15rem 0.35rem;
  }
  
  .endpoint-path {
    font-size: 0.8rem;
  }
  
  .endpoint-desc {
    font-size: 0.75rem;
  }
  
  .code-block pre {
    font-size: 0.7rem;
    padding: 0.5rem;
  }
  
  .auth-section {
    padding: 0.75rem;
    border-radius: 6px;
  }
  
  .auth-title {
    font-size: 0.85rem;
  }
  
  .auth-desc {
    font-size: 0.75rem;
  }
}
</style>
