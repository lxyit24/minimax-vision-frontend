<template>
  <div class="image-uploader" @paste="handlePaste">
    <div 
      class="upload-area"
      :class="{ 'dragover': isDragover }"
      @dragover.prevent="isDragover = true"
      @dragleave="isDragover = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileChange"
        style="display: none"
      />
      
      <div v-if="!previewUrl" class="upload-placeholder">
        <div class="upload-icon">📁</div>
        <p>点击或拖拽图片到这里上传</p>
        <p class="upload-hint">支持 PNG, JPG, WebP 格式</p>
        <p class="upload-hint paste-hint">💡 也可以直接 Ctrl+V 粘贴截图</p>
      </div>
      
      <div v-else class="upload-placeholder">
        <div class="upload-icon">✅</div>
        <p>图片已选择</p>
        <p class="upload-hint">点击可重新选择</p>
      </div>
    </div>
    
    <!-- 粘贴提示 -->
    <div v-if="showPasteToast" class="paste-toast">
      🖼️ 图片已粘贴
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{
  imageSelected: [file: File, preview: string]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragover = ref(false)
const previewUrl = ref<string>('')
const showPasteToast = ref(false)

// 显示粘贴成功提示
const displayPasteToast = () => {
  showPasteToast.value = true
  setTimeout(() => {
    showPasteToast.value = false
  }, 2000)
}

// 处理 Ctrl+V 粘贴事件
const handlePaste = (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        processFile(file)
        displayPasteToast()
        break
      }
    }
  }
}

// 全局粘贴监听（确保页面任何位置都能粘贴）
const handleGlobalPaste = (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      const file = item.getAsFile()
      if (file) {
        processFile(file)
        displayPasteToast()
        break
      }
    }
  }
}

onMounted(() => {
  document.addEventListener('paste', handleGlobalPaste)
})

onUnmounted(() => {
  document.removeEventListener('paste', handleGlobalPaste)
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  isDragover.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const preview = e.target?.result as string
    previewUrl.value = preview
    emit('imageSelected', file, preview)
  }
  reader.readAsDataURL(file)
}

// 暴露方法给父组件，用于重置状态
const reset = () => {
  previewUrl.value = ''
}

defineExpose({ reset })
</script>

<style scoped>
.image-uploader {
  width: 100%;
  position: relative;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f0f0ff;
}

.upload-area.dragover {
  border-color: #667eea;
  background: #eef0ff;
  transform: scale(1.02);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-placeholder p {
  margin: 0;
  color: #666;
}

.upload-placeholder p:first-of-type {
  font-size: 1.1rem;
  font-weight: 500;
}

.upload-hint {
  margin-top: 0.5rem !important;
  font-size: 0.9rem !important;
  color: #999 !important;
}

.paste-hint {
  color: #667eea !important;
  font-weight: 500 !important;
}

.paste-toast {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(102, 126, 234, 0.95);
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 500;
  animation: fadeInOut 2s ease;
  pointer-events: none;
  z-index: 10;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  20% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
}
</style>
