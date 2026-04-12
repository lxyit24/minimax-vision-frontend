<template>
  <div class="home">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">🔮</span>
        <span class="brand-name">MiniMax Vision</span>
        <span class="brand-badge">图片理解</span>
      </div>
      <div class="nav-actions">
        <router-link to="/docs" class="nav-link">
          📚 API 文档
        </router-link>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          AI 驱动的图片理解
        </div>
        <h1>智能图片分析<br/>只需上传即可</h1>
        <p class="hero-desc">
          基于 MiniMax 先进的多模态模型，自动识别图片中的物体、场景、文字和语义理解。支持自定义提示词，获得精准的分析结果。
        </p>
        <div class="hero-features">
          <span class="feature-tag">🌐 多语言支持</span>
          <span class="feature-tag">⚡ 快速响应</span>
          <span class="feature-tag">🔒 安全可靠</span>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card">
          <div class="card-icon">🖼️</div>
          <span>上传图片</span>
        </div>
        <div class="floating-card">
          <div class="card-icon">✨</div>
          <span>AI 分析</span>
        </div>
        <div class="floating-card">
          <div class="card-icon">📝</div>
          <span>获取结果</span>
        </div>
      </div>
    </section>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 上传区域 -->
      <section class="upload-section">
        <div class="section-header">
          <h2>📤 上传图片</h2>
          <p class="section-desc">支持 JPG、PNG、GIF、WebP 格式，最大 10MB</p>
        </div>
        <ImageUploader @image-selected="handleImageSelected" />
      </section>

      <!-- 提示词输入 -->
      <section class="prompt-section">
        <div class="section-header">
          <h2>💬 自定义提示词</h2>
          <p class="section-desc">指定你想从图片中获取什么信息</p>
        </div>
        <div class="prompt-card">
          <textarea 
            v-model="customPrompt"
            placeholder="例如：请详细描述这张图片中的场景、人物和物品..."
            rows="3"
            @keydown.ctrl.c="copyResult"
          ></textarea>
          <div class="prompt-footer">
            <span class="prompt-hint">
              💡 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 复制分析结果
            </span>
            <button class="copy-btn" @click="copyResult" :disabled="!analysisResult">
              📋 复制结果
            </button>
          </div>
        </div>
      </section>

      <!-- 图片预览 -->
      <section v-if="selectedImage" class="preview-section">
        <div class="section-header">
          <h2>📷 图片预览</h2>
          <span class="file-info">{{ selectedImage.name }} ({{ formatSize(selectedImage.size) }})</span>
        </div>
        <div class="image-preview">
          <img :src="previewUrl" alt="Preview" />
        </div>
      </section>

      <!-- 分析结果 -->
      <section v-if="analysisResult || isAnalyzing" class="result-section">
        <div class="section-header">
          <h2>📝 分析结果</h2>
          <button v-if="analysisResult" class="copy-btn" @click="copyResult">
            📋 复制结果
          </button>
        </div>
        <AnalysisResult 
          :result="analysisResult" 
          :is-loading="isAnalyzing" 
        />
      </section>
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="brand-icon">🔮</span>
          <span>MiniMax Vision API</span>
        </div>
        <p class="footer-desc">基于 MiniMax 多模态模型构建，支持文件上传、Base64、URL 多种分析方式</p>
        <div class="footer-links">
          <router-link to="/docs">API 文档</router-link>
          <span class="divider">|</span>
          <a href="https://github.com/lxyit24/minimax-vision-frontend" target="_blank">GitHub</a>
        </div>
      </div>
    </footer>

    <!-- Toast 提示 -->
    <Transition name="toast">
      <div v-if="showCopyToast" class="toast">
        ✅ 已复制到剪贴板
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AnalysisResult from '@/components/AnalysisResult.vue'
import { analyzeImage } from '@/api/analysis'

const selectedImage = ref<File | null>(null)
const previewUrl = ref<string>('')
const analysisResult = ref<string>('')
const isAnalyzing = ref(false)
const customPrompt = ref<string>('')
const showCopyToast = ref(false)

const handleImageSelected = async (file: File, preview: string) => {
  selectedImage.value = file
  previewUrl.value = preview
  
  isAnalyzing.value = true
  analysisResult.value = ''
  
  try {
    const result = await analyzeImage(file, customPrompt.value)
    analysisResult.value = result
  } catch (error) {
    analysisResult.value = `分析失败: ${error}`
  } finally {
    isAnalyzing.value = false
  }
}

const copyResult = async () => {
  if (!analysisResult.value) return
  
  try {
    await navigator.clipboard.writeText(analysisResult.value)
    showCopyToast.value = true
    setTimeout(() => { showCopyToast.value = false }, 2000)
  } catch (err) {
    const textarea = document.createElement('textarea')
    textarea.value = analysisResult.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    showCopyToast.value = true
    setTimeout(() => { showCopyToast.value = false }, 2000)
  }
}

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
/* ===== 基础变量 ===== */
.home {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #818cf8;
  --success: #10b981;
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
  background: rgba(15, 23, 42, 0.9);
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
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.nav-link:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

/* ===== Hero Section ===== */
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  padding: 4rem 3rem;
  background: var(--bg-dark);
  min-height: 400px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
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
  margin-bottom: 1.5rem;
  width: fit-content;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--primary-light);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.hero h1 {
  font-size: 2.8rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 1rem;
  line-height: 1.2;
}

.hero-desc {
  color: var(--text-secondary);
  font-size: 1.1rem;
  line-height: 1.7;
  margin: 0 0 1.5rem;
  max-width: 500px;
}

.hero-features {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.feature-tag {
  background: var(--bg-card);
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid var(--border);
}

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
}

.floating-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  animation: float 3s ease-in-out infinite;
  min-width: 120px;
}

.floating-card:nth-child(2) {
  animation-delay: 0.5s;
  transform: translateY(-10px);
}

.floating-card:nth-child(3) {
  animation-delay: 1s;
  transform: translateY(-20px);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.floating-card:nth-child(2) {
  animation: float2 3s ease-in-out infinite;
  animation-delay: 0.5s;
}

@keyframes float2 {
  0%, 100% { transform: translateY(-10px); }
  50% { transform: translateY(-20px); }
}

.floating-card:nth-child(3) {
  animation: float3 3s ease-in-out infinite;
  animation-delay: 1s;
}

@keyframes float3 {
  0%, 100% { transform: translateY(-20px); }
  50% { transform: translateY(-30px); }
}

.card-icon {
  font-size: 2rem;
}

.floating-card span {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* ===== 主内容区 ===== */
.main-content {
  padding: 2rem 3rem 4rem;
  max-width: 800px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.section-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 0;
}

.file-info {
  color: var(--text-muted);
  font-size: 0.8rem;
  background: var(--bg-card);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* ===== Section Cards ===== */
.upload-section,
.prompt-section,
.preview-section,
.result-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

/* ===== Prompt Card ===== */
.prompt-card {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.prompt-card textarea {
  width: 100%;
  padding: 1rem;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 100px;
  box-sizing: border-box;
}

.prompt-card textarea:focus {
  outline: none;
}

.prompt-card textarea::placeholder {
  color: var(--text-muted);
}

.prompt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
}

.prompt-hint {
  color: var(--text-muted);
  font-size: 0.8rem;
}

kbd {
  background: var(--bg-card);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  border: 1px solid var(--border);
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.copy-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.copy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Image Preview ===== */
.image-preview {
  display: flex;
  justify-content: center;
  background: var(--bg-code);
  border-radius: 12px;
  padding: 1rem;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}

/* ===== Footer ===== */
.footer {
  background: var(--bg-dark);
  border-top: 1px solid var(--border);
  padding: 3rem 2rem;
}

.footer-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.footer-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 0 0 1rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  align-items: center;
}

.footer-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--primary-light);
}

.footer-links .divider {
  color: var(--text-muted);
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
  .hero {
    grid-template-columns: 1fr;
    padding: 2rem;
    text-align: center;
  }
  
  .hero-content {
    align-items: center;
  }
  
  .hero-desc {
    max-width: 100%;
  }
  
  .hero-features {
    justify-content: center;
  }
  
  .hero-visual {
    margin-top: 1rem;
  }
  
  .main-content {
    padding: 1.5rem;
  }
}

@media (max-width: 600px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero-visual {
    flex-direction: column;
    gap: 1rem;
  }
  
  .floating-card {
    padding: 1.5rem 1rem;
    min-width: 100px;
  }
  
  .floating-card:nth-child(2),
  .floating-card:nth-child(3) {
    transform: none;
    animation: none;
  }
}
</style>
