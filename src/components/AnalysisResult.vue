<template>
  <div class="analysis-result">
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>AI 正在分析图片...</p>
    </div>
    
    <div v-else-if="result" class="result-content">
      <pre>{{ result }}</pre>
    </div>
    
    <div v-else class="empty">
      <p>暂无分析结果</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  result: string
  isLoading: boolean
}>()
</script>

<style scoped>
.analysis-result {
  min-height: 100px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-content {
  background: #1e293b;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
}

.result-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #f8fafc;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}
</style>
