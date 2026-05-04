<template>
  <div class="home">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">🔮</span>
        <span class="brand-name">慧眼</span>
        <span class="brand-badge">AI 助手</span>
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
          慧眼
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
          <!-- 对话历史侧边栏 -->
          <aside class="conversation-sidebar" v-if="showSidebar">
            <div class="sidebar-header">
              <h3>对话历史</h3>
              <button class="new-chat-btn" @click="createNewConversation" title="新建对话">
                ✏️ 新对话
              </button>
            </div>
            <div class="conversation-list">
              <div 
                v-for="conv in sortedConversations" 
                :key="conv.id"
                :class="['conversation-item', { active: conv.id === currentConversationId }]"
                @click="switchConversation(conv.id)"
              >
                <div class="conv-info">
                  <span class="conv-title">{{ conv.title }}</span>
                  <span class="conv-time">{{ formatTime(conv.updatedAt) }}</span>
                </div>
                <button 
                  class="delete-conv-btn" 
                  @click.stop="deleteConversation(conv.id)"
                  title="删除对话"
                >
                  🗑️
                </button>
              </div>
              <div v-if="conversations.length === 0" class="no-conversations">
                暂无对话记录
              </div>
            </div>
          </aside>
          
          <div class="chat-main">
            <!-- 切换侧边栏按钮 -->
            <button class="toggle-sidebar-btn" @click="showSidebar = !showSidebar" :title="showSidebar ? '隐藏历史' : '显示历史'">
              {{ showSidebar ? '◀' : '▶' }}
            </button>
            
            <ChatPanel 
              :messages="currentMessages"
              :is-loading="isChatLoading"
              @send-message="handleSendMessage"
              @clear-chat="handleClearChat"
              @stop="handleStop"
            />
          </div>
        </div>
      </section>
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="brand-icon">🔮</span>
          <span>慧眼</span>
        </div>
        <p class="footer-desc">基于 MiniMax 多模态模型，支持图片分析和智能对话</p>
        <div class="footer-links">
          <router-link to="/privacy">隐私政策</router-link>
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
import { ref, computed, onMounted } from 'vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AnalysisResult from '@/components/AnalysisResult.vue'
import ChatPanel from '@/components/ChatPanel.vue'
import { analyzeImage, sendChatMessageStream, clearChat } from '@/api/analysis'
import type { ChatMessage } from '@/api/analysis'

// ========== 对话历史管理 ==========

interface Conversation {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

const DEVICE_ID_KEY = 'minimax-vision-device-id'
const STORAGE_KEY_PREFIX = 'minimax-vision-conversations-'

// 获取或生成设备唯一标识
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem(DEVICE_ID_KEY)
  if (!deviceId) {
    deviceId = 'device_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9)
    localStorage.setItem(DEVICE_ID_KEY, deviceId)
  }
  return deviceId
}

// 当前设备的存储 key
const getStorageKey = (): string => {
  return STORAGE_KEY_PREFIX + getDeviceId()
}

// 对话列表
const conversations = ref<Conversation[]>([])
const currentConversationId = ref<string | null>(null)
const showSidebar = ref(true)  // 侧边栏默认显示

// 加载对话历史
const loadConversations = () => {
  try {
    const stored = localStorage.getItem(getStorageKey())
    if (stored) {
      const data = JSON.parse(stored)
      conversations.value = data.conversations || []
      currentConversationId.value = data.currentConversationId || null
    } else {
      conversations.value = []
      currentConversationId.value = null
    }
  } catch (e) {
    console.error('Failed to load conversations:', e)
    conversations.value = []
    currentConversationId.value = null
  }
}

// 保存对话历史
const saveConversations = () => {
  try {
    const data = {
      conversations: conversations.value,
      currentConversationId: currentConversationId.value
    }
    const jsonStr = JSON.stringify(data)
    // 检查大小
    if (jsonStr.length > 4 * 1024 * 1024) {
      console.warn('Conversation data too large, skipping save')
      return
    }
    localStorage.setItem(getStorageKey(), jsonStr)
  } catch (e) {
    console.error('Failed to save conversations:', e)
  }
}

// 当前对话的消息
const currentMessages = computed(() => {
  if (!currentConversationId.value) return []
  const conv = conversations.value.find(c => c.id === currentConversationId.value)
  return conv?.messages || []
})

// 排序后的对话列表（最新在前）
const sortedConversations = computed(() => {
  return [...conversations.value].sort((a, b) => b.updatedAt - a.updatedAt)
})

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 创建新对话
const createNewConversation = () => {
  const newConv: Conversation = {
    id: generateId(),
    title: '新对话',
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
  conversations.value.push(newConv)
  currentConversationId.value = newConv.id
  saveConversations()
}

// 切换对话
const switchConversation = (id: string) => {
  currentConversationId.value = id
  saveConversations()
}

// 删除对话
const deleteConversation = (id: string) => {
  const index = conversations.value.findIndex(c => c.id === id)
  if (index === -1) return
  
  conversations.value.splice(index, 1)
  
  // 如果删除的是当前对话，切换到另一个或创建新对话
  if (currentConversationId.value === id) {
    if (conversations.value.length > 0) {
      currentConversationId.value = conversations.value[0].id
    } else {
      // 没有对话了，创建新对话
      createNewConversation()
    }
  }
  saveConversations()
}

// 确保有当前对话
const ensureCurrentConversation = () => {
  if (!currentConversationId.value || !conversations.value.find(c => c.id === currentConversationId.value)) {
    if (conversations.value.length === 0) {
      createNewConversation()
    } else {
      currentConversationId.value = conversations.value[0].id
    }
  }
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  const now = Date.now()
  const diff = now - timestamp
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  
  if (diff < minute) return '刚刚'
  if (diff < hour) return Math.floor(diff / minute) + '分钟前'
  if (diff < day) return Math.floor(diff / hour) + '小时前'
  if (diff < 7 * day) return Math.floor(diff / day) + '天前'
  
  const date = new Date(timestamp)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// ========== 原有功能 ==========

// Tab state
const activeTab = ref<'analyze' | 'chat'>('analyze')

// Analyze mode state
const selectedImage = ref<File | null>(null)
const previewUrl = ref<string>('')
const analysisResult = ref<string>('')
const isAnalyzing = ref(false)
const customPrompt = ref<string>('')

// Chat mode state
const isChatLoading = ref(false)
const chatSessionId = ref('default')
const abortController = ref<AbortController | null>(null)

// Toast
const showCopyToast = ref(false)

// 页面加载时恢复对话历史
onMounted(() => {
  loadConversations()
  ensureCurrentConversation()
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
  // 确保有当前对话
  ensureCurrentConversation()
  
  // 获取当前对话
  const conv = conversations.value.find(c => c.id === currentConversationId.value)
  if (!conv) return
  
  // 添加用户消息
  const userMsg: ChatMessage = { role: 'user', content: message, image }
  conv.messages.push(userMsg)
  conv.updatedAt = Date.now()
  
  // 添加空的助手消息占位符
  const assistantMsgIndex = conv.messages.length
  conv.messages.push({ role: 'assistant', content: '' })
  
  isChatLoading.value = true
  saveConversations()
  
  // 创建 AbortController 用于取消请求
  abortController.value = new AbortController()
  let streamError = false
  
  try {
    await sendChatMessageStream(
      message,
      // onChunk: 更新消息内容
      (chunk) => {
        const c = conversations.value.find(c => c.id === currentConversationId.value)
        if (c && c.messages[assistantMsgIndex]) {
          c.messages[assistantMsgIndex].content += chunk
          saveConversations()
        }
      },
      // onError: 处理错误
      image,
      chatSessionId.value,
      (error) => {
        streamError = true
        const c = conversations.value.find(c => c.id === currentConversationId.value)
        if (c && c.messages[assistantMsgIndex]) {
          c.messages[assistantMsgIndex].content = `抱歉，发生了错误: ${error}`
          saveConversations()
        }
      },
      // onDone: 完成
      () => {
        // 流式结束，不做任何事（内容已经通过 onChunk 更新）
      },
      // Pass the AbortSignal
      abortController.value.signal
    )
  } catch (error: any) {
    // Check if it's an abort error
    if (error?.name === 'AbortError' || error?.message?.includes('abort')) {
      const c = conversations.value.find(c => c.id === currentConversationId.value)
      if (c && c.messages[assistantMsgIndex] && !c.messages[assistantMsgIndex].content) {
        c.messages[assistantMsgIndex].content = '[已停止]'
        saveConversations()
      }
    } else if (!streamError) {
      const c = conversations.value.find(c => c.id === currentConversationId.value)
      if (c && c.messages[assistantMsgIndex]) {
        c.messages[assistantMsgIndex].content = `网络错误: ${error}`
        saveConversations()
      }
    }
  } finally {
    isChatLoading.value = false
    abortController.value = null
  }
}

const handleStop = () => {
  if (abortController.value) {
    abortController.value.abort()
  }
}

const handleClearChat = async () => {
  try {
    await clearChat(chatSessionId.value)
  } catch (error) {
    console.error('Clear chat error:', error)
  }
  
  // 清空当前对话的消息
  const conv = conversations.value.find(c => c.id === currentConversationId.value)
  if (conv) {
    conv.messages = []
    conv.title = '新对话'
    conv.updatedAt = Date.now()
    saveConversations()
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
  display: flex;
  gap: 0.5rem;
}

/* ========== 对话历史侧边栏 ========== */
.conversation-sidebar {
  width: 240px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 600;
}

.new-chat-btn {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: var(--primary-dark);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0.25rem;
}

.conversation-item:hover {
  background: rgba(99, 102, 241, 0.15);
}

.conversation-item.active {
  background: rgba(99, 102, 241, 0.25);
  border: 1px solid var(--primary);
}

.conv-info {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.conv-title {
  font-size: 0.85rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-time {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.delete-conv-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.25rem;
  opacity: 0;
  transition: all 0.2s;
  border-radius: 4px;
}

.conversation-item:hover .delete-conv-btn {
  opacity: 1;
}

.delete-conv-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.no-conversations {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 2rem 1rem;
}

/* 切换侧边栏按钮 */
.toggle-sidebar-btn {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: none;
  color: var(--text-secondary);
  padding: 0.5rem 0.3rem;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  font-size: 0.7rem;
  z-index: 10;
  transition: all 0.2s;
}

.toggle-sidebar-btn:hover {
  background: var(--border);
  color: var(--text-primary);
}

.chat-main {
  flex: 1;
  position: relative;
  min-width: 0;
}

/* ========== Section Cards ========== */
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
  .top-nav {
    gap: 0.25rem;
    padding: 0.4rem 0.5rem;
  }
  
  .nav-brand {
    font-size: 0.9rem;
  }
  
  .nav-tabs {
    gap: 0.15rem;
  }
  
  .nav-tab {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
  }
  
  .hero {
    padding: 0.6rem 0.5rem;
  }
  
  .hero-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
    margin-bottom: 0.4rem;
  }
  
  .hero h1 {
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
  }
  
  .hero-desc {
    font-size: 0.75rem;
    display: none;
  }
  
  .main-content {
    padding: 0.5rem 0.35rem 0.5rem;
    min-height: auto;
    height: calc(100dvh - 120px);
    display: flex;
    flex-direction: column;
  }
  
  .tab-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .chat-wrapper {
    flex-direction: column;
    height: 100%;
  }
  
  .conversation-sidebar {
    width: 100%;
    height: 120px;
    flex-shrink: 0;
  }
  
  .conversation-list {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.5rem;
    gap: 0.5rem;
  }
  
  .conversation-item {
    flex-shrink: 0;
    width: 140px;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .delete-conv-btn {
    opacity: 1;
  }
  
  .upload-section,
  .prompt-section,
  .preview-section,
  .result-section {
    padding: 0.5rem;
    margin-bottom: 0.4rem;
    border-radius: 8px;
  }
  
  .section-header {
    margin-bottom: 0.4rem;
  }
  
  .section-header h2 {
    font-size: 0.85rem;
  }
  
  .preview-section {
    order: -1;
    flex-shrink: 0;
  }
  
  .preview-image {
    max-height: 100px;
  }
  
  .result-section {
    flex: 1;
    overflow: auto;
  }
  
  .result-text {
    max-height: none;
    font-size: 0.8rem;
  }
  
  .prompt-card {
    border-radius: 6px;
    flex-shrink: 0;
  }
  
  textarea.prompt-input {
    font-size: 16px;
    min-height: 50px;
    padding: 0.4rem 0.5rem;
  }
  
  .copy-btn {
    top: 0.25rem;
    right: 0.25rem;
    padding: 0.2rem 0.4rem;
    font-size: 0.65rem;
  }
  
  .footer {
    padding: 0.4rem 0.5rem;
    font-size: 0.65rem;
    gap: 0.15rem;
  }
  
  .footer a {
    font-size: 0.65rem;
  }
}

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
}
</style>
