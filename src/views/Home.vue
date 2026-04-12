<template>
  <div class="home">
    <header class="header">
      <h1>🖼️ MiniMax 图片理解</h1>
      <p>上传图片，AI 智能分析内容</p>
    </header>

    <main class="main-content">
      <div class="upload-section">
        <ImageUploader @image-selected="handleImageSelected" />
      </div>

      <!-- 提示词输入框 -->
      <div class="prompt-section">
        <h2>💬 自定义提示词</h2>
        <div class="prompt-input-wrapper">
          <textarea 
            v-model="customPrompt"
            placeholder="输入你想让 AI 分析的内容... (可选，默认会详细描述图片)"
            rows="3"
            @keydown.ctrl.c="copyResult"
          ></textarea>
          <div class="prompt-hint">
            <span>按 Ctrl+C 复制分析结果</span>
            <button class="copy-btn" @click="copyResult" title="复制结果">
              📋 复制
            </button>
          </div>
        </div>
      </div>

      <div v-if="selectedImage" class="preview-section">
        <h2>📷 图片预览</h2>
        <div class="image-preview">
          <img :src="previewUrl" alt="Preview" />
        </div>
      </div>

      <div v-if="analysisResult || isAnalyzing" class="result-section">
        <div class="result-header">
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
    </main>

    <footer class="footer">
      <p>Powered by MiniMax Vision API + OpenClaw MCP</p>
    </footer>

    <!-- 复制成功提示 -->
    <div v-if="showCopyToast" class="copy-toast">
      ✅ 已复制到剪贴板
    </div>
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
  
  // Start analysis
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
    setTimeout(() => {
      showCopyToast.value = false
    }, 2000)
  } catch (err) {
    // Fallback for older browsers
    const textarea = document.createElement('textarea')
    textarea.value = analysisResult.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    showCopyToast.value = true
    setTimeout(() => {
      showCopyToast.value = false
    }, 2000)
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  padding: 2rem;
  text-align: center;
  color: white;
}

.header h1 {
  margin: 0;
  font-size: 2.5rem;
}

.header p {
  margin: 0.5rem 0 0;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.upload-section,
.prompt-section,
.preview-section,
.result-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

h2 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1.2rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.result-header h2 {
  margin: 0;
}

.prompt-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 80px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

.prompt-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #888;
}

.copy-btn {
  padding: 0.4rem 0.8rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.copy-btn:hover {
  background: #5568d3;
}

.image-preview {
  display: flex;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 1rem;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.footer {
  padding: 1.5rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.copy-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
