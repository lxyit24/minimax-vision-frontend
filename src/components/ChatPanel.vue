<template>
  <div class="chat-panel">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="chat-title">
        <span class="chat-icon">🤖</span>
        <span>MiniMax Vision 智能助手</span>
      </div>
      <div class="chat-actions">
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
        <h3>欢迎使用 MiniMax Vision 智能助手</h3>
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
          <!-- 文字 -->
          <div class="message-text">{{ msg.content }}</div>
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

        <!-- 发送按钮 -->
        <button 
          class="send-btn" 
          @click="sendMessage"
          :disabled="!canSend"
        >
          ➤
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  image?: string
}

const emit = defineEmits<{
  (e: 'send-message', message: string, image?: string): void
  (e: 'clear-chat'): void
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

function clearChat() {
  emit('clear-chat')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
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

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .chat-messages {
    padding: 0.75rem;
  }
  
  .welcome-message {
    padding: 1.5rem 1rem;
  }
  
  .welcome-icon {
    font-size: 2.5rem;
  }
  
  .welcome-title {
    font-size: 1rem;
  }
  
  .welcome-desc {
    font-size: 0.85rem;
  }
  
  .message {
    margin-bottom: 0.75rem;
  }
  
  .message-content {
    max-width: 85%;
    padding: 0.6rem 0.85rem;
    font-size: 0.9rem;
    border-radius: 14px;
  }
  
  .user-message .message-content {
    border-radius: 14px 14px 4px 14px;
  }
  
  .assistant-message .message-content {
    border-radius: 14px 14px 14px 4px;
  }
  
  .message-time {
    font-size: 0.65rem;
    margin-top: 0.25rem;
  }
  
  .typing-indicator {
    padding: 0.6rem 0.85rem;
  }
  
  .typing-dot {
    width: 6px;
    height: 6px;
  }
  
  .input-row {
    gap: 0.5rem;
    padding: 0.75rem;
  }
  
  .attach-btn,
  .send-btn {
    width: 38px;
    height: 38px;
    border-radius: 8px;
  }
  
  textarea {
    padding: 0.6rem 0.75rem;
    font-size: 16px; /* 防止iOS缩放 */
    border-radius: 8px;
    min-height: 38px;
    max-height: 100px;
  }
  
  .attached-image-preview {
    max-width: 120px;
    max-height: 120px;
  }
  
  .remove-image {
    width: 18px;
    height: 18px;
    font-size: 10px;
    top: -6px;
    right: -6px;
  }
}

/* 小屏幕手机 */
@media (max-width: 480px) {
  .chat-messages {
    padding: 0.5rem;
  }
  
  .message-content {
    max-width: 88%;
    padding: 0.5rem 0.7rem;
    font-size: 0.875rem;
  }
  
  .welcome-icon {
    font-size: 2rem;
  }
  
  .welcome-title {
    font-size: 0.9rem;
  }
  
  .welcome-desc {
    font-size: 0.8rem;
    line-height: 1.4;
  }
  
  .input-row {
    padding: 0.5rem;
  }
  
  textarea {
    font-size: 16px;
  }
  
  .attached-image-preview {
    max-width: 100px;
    max-height: 100px;
  }
}
</style>
