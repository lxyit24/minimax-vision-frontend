import axios from 'axios'

// Use relative URL - nginx proxies /api/* to backend on port 5001
const API_BASE = ''

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  image?: string
}

export interface ChatResponse {
  success: boolean
  response: string
  session_id: string
  history: ChatMessage[]
  error?: string
}

export async function analyzeImage(file: File, prompt?: string): Promise<string> {
  const formData = new FormData()
  formData.append('image', file)
  if (prompt) {
    formData.append('prompt', prompt)
  }
  
  const response = await axios.post(`${API_BASE}/api/analyze`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 120000 // 2 minutes timeout for image analysis
  })
  
  return response.data.result
}

export async function sendChatMessage(
  message: string,
  image?: string,
  sessionId?: string
): Promise<ChatResponse> {
  const response = await axios.post(`${API_BASE}/api/chat`, {
    message,
    image,
    session_id: sessionId || undefined
  }, {
    headers: {
      'Content-Type': 'application/json'
    },
    timeout: 120000 // 2 minutes timeout
  })
  
  return response.data
}

export async function clearChat(sessionId?: string): Promise<void> {
  await axios.post(`${API_BASE}/api/chat/clear`, {
    session_id: sessionId || undefined
  }, {
    headers: {}
  })
}
