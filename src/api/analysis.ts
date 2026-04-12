import axios from 'axios'

// Direct backend URL to bypass Vite proxy issues
const API_BASE = 'http://localhost:5001'

// API Key for external access
const API_KEY = 'minimax-vision-api-key-2024'

// Helper to create headers
const getHeaders = () => ({
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
})

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
  
  const response = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: {
      'X-API-Key': API_KEY,
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
    session_id: sessionId || 'default'
  }, {
    headers: getHeaders(),
    timeout: 120000 // 2 minutes timeout
  })
  
  return response.data
}

export async function clearChat(sessionId?: string): Promise<void> {
  await axios.post(`${API_BASE}/api/chat/clear`, {
    session_id: sessionId || 'default'
  }, {
    headers: getHeaders()
  })
}
