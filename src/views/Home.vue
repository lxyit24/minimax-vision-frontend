<template>
  <div class="home">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">🔮</span>
        <span class="brand-name">MiniMax Vision</span>
        <span class="brand-badge">智能体</span>
      </div>
      <div class="nav-tabs">
        <button 
          :class="['nav-tab', { active: activeTab === 'analyze' }]"
          @click="activeTab = 'analyze'"
        >
          📊 图片分析
        </button>
        <button 
          :class="['nav-tab', { active: activeTab === 'chat' }]"
          @click="activeTab = 'chat'"
        >
          💬 AI 对话
        </button>
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
          AI 智能体
        </div>
        <h1>图片理解智能助手</h1>
        <p class="hero-desc">
          基于 MiniMax 多模态模型的 AI 智能体，可以分析图片内容并与你进行智能对话。切换到对话模式，体验更自然的交互方式。
        </p>
      </div>
    </section>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- ========== 图片分析模式 ========== -->
      <section v-show="activeTab === 'analyze'" class="tab-content">
        <div class="upload-section">
          <div class="section-header">
            <h2>📤 上传图片</h2>
            <p class="section-desc">支持 JPG、PNG、GIF、WebP 格式，最大 10MB</p>
          </div>
          <ImageUploader @image-selected="handleImageSelected" />
        </div>

        <div class="prompt-section">
          <div class="section-header">
            <h2>💬 自定义提示词</h2>
            <p class="section-desc">指定你想从图片中获取什么信息</p>
          </div>
          <div class="prompt-card">
            <textarea 
              v-model="customPrompt"
              placeholder="例如：请详细描述这张图片中的场景、人物和物品..."
              rows="3"
            ></textarea>
            <div class="prompt-footer">
              <span class="prompt-hint">
                💡 可与图片一起发送，获得精准分析
              </span>
            </div>
          </div>
        </div>

        <div v-if="selectedImage" class="preview-section">
          <div class="section-header">
            <h2>📷 图片预览</h2>
            <span class="file-info">{{ selectedImage.name }} ({{ formatSize(selectedImage.size) }})</span>
          </div>
          <div class="image-preview">
            <img :src="previewUrl" alt="Preview" />
          </div>
        </div>

        <div v-if="analysisResult || isAnalyzing" class="result-section">
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
        </div>
      </section>

      <!-- ========== AI 对话模式 ========== -->
      <section v-show="activeTab === 'chat'" class="tab-content chat-tab">
        <div class="chat-wrapper">
          <ChatPanel 
            :messages="chatMessages"
            :is-loading="isChatLoading"
            @send-message="handleSendMessage"
            @clear-chat="handleClearChat"
          />
        </div>
      </section>
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="brand-icon">🔮</span>
          <span>MiniMax Vision 智能体</span>
        </div>
        <p class="footer-desc">基于 MiniMax 多模态模型，支持图片分析和智能对话</p>
        <div class="footer-links">
          <router-link to="/docs">API 文档</router-link>
          <span class="divider">|</span>
          <span>Copyright © 2023-2026 六仙云</span>
          <span class="divider">|</span>
          <a href="https://beian.miit.gov.cn/" target="_blank">鲁ICP备2025137668号</a>
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
import { ref, watchEffect, onMounted } from 'vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AnalysisResult from '@/components/AnalysisResult.vue'
import ChatPanel from '@/components/ChatPanel.vue'
import { analyzeImage, sendChatMessage, clearChat } from '@/api/analysis'
import type { ChatMessage } from '@/api/analysis'

// Tab state
const activeTab = ref<'analyze' | 'chat'>('analyze')

// Analyze mode state
const selectedImage = ref<File | null>(null)
const previewUrl = ref<string>('')
const analysisResult = ref<string>('')
const isAnalyzing = ref(false)
const customPrompt = ref<string>('')

// Chat mode state
const chatMessages = ref<ChatMessage[]>([])
const isChatLoading = ref(false)
const chatSessionId = ref('default')

// Toast
const showCopyToast = ref(false)

// localStorage key for chat messages
const CHAT_STORAGE_KEY = 'minimax-vision-chat-messages'

// 从 localStorage 加载聊天记录
const loadChatFromStorage = () => {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY)
    if (stored) {
      const messages = JSON.parse(stored)
      if (Array.isArray(messages)) {
        chatMessages.value = messages
      }
    }
  } catch (e) {
    console.error('Failed to load chat from localStorage:', e)
  }
}

// 保存聊天记录到 localStorage
const saveChatToStorage = () => {
  try {
    const data = JSON.stringify(chatMessages.value)
    // 检查大小，避免超出 localStorage 限制（约5MB）
    if (data.length > 4 * 1024 * 1024) {
      console.warn('Chat data too large for localStorage, skipping save')
      return
    }
    localStorage.setItem(CHAT_STORAGE_KEY, data)
  } catch (e) {
    console.error('Failed to save chat to localStorage:', e)
  }
}

// 页面加载时从 localStorage 恢复聊天记录
onMounted(() => {
  loadChatFromStorage()
})

// 监听聊天消息变化，自动保存到 localStorage
watchEffect(() => {
  // 追踪 chatMessages.value 的依赖
  const messages = chatMessages.value
  if (messages.length > 0) {
    saveChatToStorage()
  }
})

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

const handleSendMessage = async (message: string, image?: string) => {
  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: message,
    image
  })
  
  isChatLoading.value = true
  
  try {
    const response = await sendChatMessage(message, image, chatSessionId.value)
    
    if (response.success) {
      // 添加助手回复
      chatMessages.value.push({
        role: 'assistant',
        content: response.response
      })
    } else {
      chatMessages.value.push({
        role: 'assistant',
        content: `抱歉，发生了错误: ${response.error}`
      })
    }
  } catch (error) {
    chatMessages.value.push({
      role: 'assistant',
      content: `网络错误: ${error}`
    })
  } finally {
    isChatLoading.value = false
  }
}

const handleClearChat = async () => {
  try {
    await clearChat(chatSessionId.value)
    chatMessages.value = []
    // 清除 localStorage 中的聊天记录
    localStorage.removeItem(CHAT_STORAGE_KEY)
  } catch (error) {
    console.error('Clear chat error:', error)
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
  background: rgba(15, 23, 42, 0.95);
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

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-card);
  padding: 0.25rem;
  border-radius: 10px;
}

.nav-tab {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-tab:hover {
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--primary);
  color: white;
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
  padding: 2rem 3rem;
  background: var(--bg-dark);
  border-bottom: 1px solid var(--border);
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
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
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.hero h1 {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
}

.hero-desc {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

/* ===== 主内容区 ===== */
.main-content {
  padding: 2rem 3rem 4rem;
  max-width: 1000px;
  margin: 0 auto;
  min-height: 60vh;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.chat-tab {
  height: calc(100vh - 300px);
  min-height: 500px;
}

.chat-wrapper {
  height: 100%;
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

/* ===== Copy Button ===== */
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

.copy-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

/* ===== Footer ===== */
.footer {
  background: var(--bg-dark);
  border-top: 1px solid var(--border);
  padding: 2rem;
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
  margin-bottom: 0.5rem;
}

.footer-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin: 0 0 1rem;
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
@media (max-width: 768px) {
  /* 导航栏 */
  .top-nav {
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
  }
  
  .nav-brand {
    font-size: 1rem;
  }
  
  .nav-tabs {
    order: 3;
    width: 100%;
    justify-content: center;
    gap: 0.25rem;
  }
  
  .nav-tab {
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
  }
  
  /* Hero - 更紧凑 */
  .hero {
    padding: 1rem 0.75rem;
  }
  
  .hero h1 {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
  }
  
  .hero-desc {
    font-size: 0.85rem;
    margin: 0;
  }
  
  .hero-badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    margin-bottom: 0.75rem;
  }
  
  /* 主内容 - 显示更多 */
  .main-content {
    padding: 0.75rem 0.5rem 4rem;
  }
  
  /* 卡片 - 更紧凑 */
  .upload-section,
  .prompt-section,
  .preview-section,
  .result-section {
    padding: 0.85rem;
    margin-bottom: 0.75rem;
    border-radius: 10px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    margin-bottom: 0.75rem;
  }
  
  .section-header h2 {
    font-size: 0.95rem;
  }
  
  /* 分析模式 */
  .analyze-grid {
    grid-template-columns: 1fr !important;
    gap: 0.75rem;
  }
  
  .preview-section {
    order: -1;
  }
  
  .preview-image {
    max-height: 160px;
  }
  
  .result-text {
    max-height: 200px;
    font-size: 0.85rem;
  }
  
  /* 对话模式 - 显示更多 */
  .chat-tab {
    min-height: auto;
    height: calc(100vh - 220px);
  }
  
  /* 提示词输入 */
  .prompt-card {
    border-radius: 8px;
  }
  
  textarea.prompt-input {
    font-size: 16px;
    min-height: 60px;
    padding: 0.6rem 0.75rem;
  }
  
  /* 复制按钮 */
  .copy-btn {
    top: 0.35rem;
    right: 0.35rem;
    padding: 0.3rem 0.5rem;
    font-size: 0.7rem;
  }
  
  /* 底部 */
  .footer {
    padding: 0.75rem 0.5rem;
    font-size: 0.7rem;
    flex-direction: column;
    gap: 0.25rem;
    text-align: center;
  }
}

/* 小屏幕手机 - 更紧凑 */
@media (max-width: 480px) {
  .hero {
    padding: 0.75rem 0.5rem;
  }
  
  .hero h1 {
    font-size: 1.1rem;
  }
  
  .hero-desc {
    font-size: 0.8rem;
  }
  
  .main-content {
    padding: 0.5rem 0.35rem 5rem;
  }
  
  .upload-section,
  .prompt-section,
  .preview-section,
  .result-section {
    padding: 0.65rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }
  
  .analyze-grid {
    gap: 0.5rem;
  }
  
  .preview-image {
    max-height: 140px;
  }
  
  .file-info {
    font-size: 0.65rem;
  }
  
  .result-text {
    max-height: 180px;
    font-size: 0.8rem;
  }
  
  .chat-tab {
    height: calc(100vh - 200px);
  }
  
  .nav-brand {
    font-size: 0.9rem;
  }
  
  .nav-tab {
    padding: 0.35rem 0.6rem;
    font-size: 0.8rem;
  }
}
</style>
