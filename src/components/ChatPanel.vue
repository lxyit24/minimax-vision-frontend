<template>
  <div class="chat-panel" :class="{ fullscreen: isFullscreen }">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="chat-title">
        <span class="chat-icon">🤖</span>
        <span>慧眼 智能助手</span>
      </div>
      <div class="chat-actions">
        <button class="action-btn" :class="{ 'fullscreen-active': isFullscreen }" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏'">
          {{ isFullscreen ? '✖' : '⛶' }}
        </button>
        <button class="action-btn" @click="clearChat" title="清除对话">
          🗑️ 清除
        </button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">👋</div>
        <h3>欢迎使用 慧眼 智能助手</h3>
        <p>我可以帮你分析图片内容，只需发送图片并描述你想了解的信息即可。</p>
        <div class="welcome-tips">
          <span class="tip">💡 发送图片 + 问题 = 分析图片</span>
          <span class="tip">💬 直接提问 = 智能对话</span>
        </div>
      </div>

      <!-- 消息 -->
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <!-- 图片 -->
          <div v-if="msg.image" class="message-image">
            <img :src="msg.image" alt="Attached image" />
          </div>
          <!-- 文字 (支持 Markdown 和 HTML) -->
          <div class="message-text" v-html="renderContent(msg.content)"></div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <!-- 图片预览 -->
      <div v-if="attachedImage" class="attached-image-preview">
        <img :src="attachedImage" alt="Attached" />
        <button class="remove-image" @click="removeImage">×</button>
      </div>

      <div class="input-row">
        <!-- 图片上传 -->
        <label class="attach-btn" title="添加图片">
          <input 
            type="file" 
            accept="image/*" 
            @change="handleImageAttach" 
          />
          📷
        </label>

        <!-- 文字输入 -->
        <textarea
          v-model="inputText"
          placeholder="输入消息，或描述你想分析的图片..."
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          ref="inputArea"
        ></textarea>

        <!-- 发送/停止按钮 -->
        <button 
          class="send-btn" 
          :class="{ 'stop-btn': isLoading }"
          @click="isLoading ? stopRequest() : sendMessage()"
          :disabled="!canSend && !isLoading"
        >
          {{ isLoading ? '⏹' : '➤' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// Configure marked
marked.setOptions({
  breaks: true,  // Convert line breaks to <br>
  gfm: true,     // GitHub Flavored Markdown
})

// Render markdown/HTML content safely
function renderContent(content: string): string {
  if (!content) return ''
  
  // Check if content contains HTML tags
  const containsHtml = /<[a-z][\s\S]*>/i.test(content)
  
  if (containsHtml) {
    // Sanitize HTML content
    return DOMPurify.sanitize(content, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'span', 'div'],
      ALLOWED_ATTR: ['href', 'target', 'class', 'style'],
    })
  } else {
    // Parse markdown
    return DOMPurify.sanitize(marked.parse(content) as string)
  }
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  image?: string
}

const emit = defineEmits<{
  (e: 'send-message', message: string, image?: string): void
  (e: 'clear-chat'): void
  (e: 'stop'): void
}>()

const props = defineProps<{
  messages: Message[]
  isLoading: boolean
}>()

const inputText = ref('')
const attachedImage = ref<string>('')
const attachedImageFile = ref<File | null>(null)
const inputArea = ref<HTMLTextAreaElement | null>(null)
const messagesContainer = ref<HTMLDivElement | null>(null)
const isFullscreen = ref(false)

const canSend = computed(() => {
  return (inputText.value.trim() || attachedImage.value) && !props.isLoading
})

function autoResize() {
  if (inputArea.value) {
    inputArea.value.style.height = 'auto'
    inputArea.value.style.height = inputArea.value.scrollHeight + 'px'
  }
}

function handleImageAttach(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    attachedImageFile.value = file
    
    // 生成预览 URL
    const reader = new FileReader()
    reader.onload = (e) => {
      attachedImage.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
  
  // 清空 input 以允许重复选择同一文件
  target.value = ''
}

function removeImage() {
  attachedImage.value = ''
  attachedImageFile.value = null
}

// 处理 Ctrl+V 粘贴图片
function handlePaste(event: ClipboardEvent) {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      const file = item.getAsFile()
      if (file) {
        attachedImageFile.value = file
        const reader = new FileReader()
        reader.onload = (e) => {
          attachedImage.value = e.target?.result as string
        }
        reader.readAsDataURL(file)
        break
      }
    }
  }
}

// 注册/取消注册全局 paste 监听
onMounted(() => {
  document.addEventListener('paste', handlePaste)
})

onUnmounted(() => {
  document.removeEventListener('paste', handlePaste)
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

async function sendMessage() {
  if (!canSend.value) return
  
  const message = inputText.value.trim()
  const image = attachedImage.value || undefined
  
  if (!message && !image) return
  
  // 清空输入
  inputText.value = ''
  attachedImage.value = ''
  attachedImageFile.value = null
  
  if (inputArea.value) {
    inputArea.value.style.height = 'auto'
  }
  
  emit('send-message', message, image)
}

function stopRequest() {
  emit('stop')
}

function clearChat() {
  emit('clear-chat')
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  
  if (isFullscreen.value) {
    // 全屏模式：添加 body 锁定防止背景滚动
    document.body.style.overflow = 'hidden'
  } else {
    // 退出全屏：恢复滚动
    document.body.style.overflow = ''
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)

// Escape 键退出全屏
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
    document.body.style.overflow = ''
  }
}

watch(isFullscreen, (newVal) => {
  if (newVal) {
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card, #1e293b);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border, #334155);
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--border, #334155);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-primary, #f8fafc);
}

.chat-icon {
  font-size: 1.25rem;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: transparent;
  border: 1px solid var(--border, #334155);
  color: var(--text-secondary, #94a3b8);
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--border, #334155);
  color: var(--text-primary, #f8fafc);
}

/* 消息列表 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary, #94a3b8);
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.welcome-message h3 {
  margin: 0 0 0.5rem;
  color: var(--text-primary, #f8fafc);
  font-size: 1.2rem;
}

.welcome-message p {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
}

.welcome-tips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.tip {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-light, #818cf8);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

/* 消息 */
.message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.message.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message.user .message-content {
  align-items: flex-end;
}

/* 消息图片 */
.message-image {
  max-width: 250px;
  border-radius: 12px;
  overflow: hidden;
}

.message-image img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 12px;
}

/* 消息文字 */
.message-text {
  background: var(--bg-code, #0d1117);
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border, #334155);
  color: var(--text-primary, #f8fafc);
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .message-text {
  background: var(--primary, #6366f1);
  border-color: var(--primary, #6366f1);
}

/* Markdown/HTML 内容样式 */
.message-text p {
  margin: 0 0 0.5rem 0;
}

.message-text p:last-child {
  margin-bottom: 0;
}

.message-text a {
  color: var(--primary-light, #818cf8);
  text-decoration: underline;
}

.message-text a:hover {
  color: var(--primary, #6366f1);
}

.message-text strong, .message-text b {
  font-weight: 600;
}

.message-text em, .message-text i {
  font-style: italic;
}

.message-text code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85em;
}

.message.user .message-text code {
  background: rgba(255, 255, 255, 0.15);
}

.message-text pre {
  background: rgba(0, 0, 0, 0.4);
  padding: 0.75rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.message-text pre code {
  background: transparent;
  padding: 0;
  font-size: 0.85rem;
}

.message-text ul, .message-text ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message-text li {
  margin: 0.25rem 0;
}

.message-text blockquote {
  border-left: 3px solid var(--primary, #6366f1);
  margin: 0.5rem 0;
  padding-left: 1rem;
  color: var(--text-secondary, #94a3b8);
}

.message-text h1, .message-text h2, .message-text h3,
.message-text h4, .message-text h5, .message-text h6 {
  margin: 0.75rem 0 0.5rem 0;
  font-weight: 600;
}

.message-text h1 { font-size: 1.25rem; }
.message-text h2 { font-size: 1.15rem; }
.message-text h3 { font-size: 1.05rem; }

.message-text span {
  /* Allow span for inline styling */
}

.message-text div {
  margin: 0.25rem 0;
}

/* 加载中 */
.message.loading .message-text {
  padding: 1rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 0.5rem;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-muted, #64748b);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { 
    transform: translateY(0);
    opacity: 0.4;
  }
  30% { 
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* 输入区域 */
.chat-input-area {
  padding: 1rem;
  border-top: 1px solid var(--border, #334155);
  background: rgba(0, 0, 0, 0.1);
}

/* 图片预览 */
.attached-image-preview {
  position: relative;
  display: inline-block;
  margin-bottom: 0.75rem;
}

.attached-image-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid var(--primary, #6366f1);
}

.remove-image {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: var(--error, #ef4444);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-image:hover {
  background: #dc2626;
}

/* 输入行 */
.input-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.attach-btn {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-code, #0d1117);
  border: 1px solid var(--border, #334155);
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
  flex-shrink: 0;
}

.attach-btn:hover {
  background: var(--border, #334155);
}

.attach-btn input {
  display: none;
}

textarea {
  flex: 1;
  padding: 0.75rem 1rem;
  background: var(--bg-code, #0d1117);
  border: 1px solid var(--border, #334155);
  border-radius: 10px;
  color: var(--text-primary, #f8fafc);
  font-family: inherit;
  font-size: 0.9rem;
  resize: none;
  min-height: 42px;
  max-height: 120px;
  line-height: 1.4;
}

textarea:focus {
  outline: none;
  border-color: var(--primary, #6366f1);
}

textarea::placeholder {
  color: var(--text-muted, #64748b);
}

.send-btn {
  width: 42px;
  height: 42px;
  background: var(--primary, #6366f1);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-dark, #4f46e5);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 停止按钮样式 */
.send-btn.stop-btn {
  background: var(--error, #ef4444);
}

.send-btn.stop-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}

/* ===== 全屏模式 ===== */
.chat-panel.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
  background: var(--bg-primary, #0f172a);
}

.chat-panel.fullscreen .chat-header {
  background: rgba(0, 0, 0, 0.3);
}

/* 全屏按钮激活状态 */
.action-btn.fullscreen-active {
  background: var(--primary, #6366f1);
  border-color: var(--primary, #6366f1);
  color: white;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .chat-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .chat-messages {
    flex: 1;
    padding: 0.4rem;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .welcome-message {
    padding: 0.75rem 0.5rem;
  }
  
  .welcome-icon {
    font-size: 1.75rem;
  }
  
  .welcome-title {
    font-size: 0.85rem;
  }
  
  .welcome-desc {
    font-size: 0.75rem;
  }
  
  .message {
    margin-bottom: 0.4rem;
  }
  
  .message-content {
    max-width: 90%;
    padding: 0.4rem 0.6rem;
    font-size: 0.85rem;
    border-radius: 10px;
  }
  
  .user-message .message-content {
    border-radius: 10px 10px 3px 10px;
  }
  
  .assistant-message .message-content {
    border-radius: 10px 10px 10px 3px;
  }
  
  .message-time {
    font-size: 0.55rem;
    margin-top: 0.1rem;
  }
  
  .typing-indicator {
    padding: 0.4rem 0.6rem;
  }
  
  .typing-dot {
    width: 4px;
    height: 4px;
  }
  
  .input-area {
    flex-shrink: 0;
    border-top: 1px solid var(--border);
    padding: 0.5rem;
  }
  
  .input-row {
    gap: 0.35rem;
  }
  
  .attach-btn,
  .send-btn {
    width: 34px;
    height: 34px;
    border-radius: 7px;
    font-size: 1rem;
  }
  
  textarea {
    padding: 0.4rem 0.55rem;
    font-size: 16px;
    border-radius: 7px;
    min-height: 34px;
    max-height: 70px;
  }
  
  .attached-image-preview {
    max-width: 70px;
    max-height: 70px;
    border-radius: 6px;
  }
  
  .remove-image {
    width: 14px;
    height: 14px;
    font-size: 8px;
    top: -4px;
    right: -4px;
  }
}
</style>
