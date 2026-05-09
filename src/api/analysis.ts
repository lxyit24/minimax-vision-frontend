import axios from 'axios'

// Use relative URL - nginx proxies /api/* to backend on port 5001
const API_BASE = ''

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  image?: string
  reasoning?: string  // 思考过程
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

export async function sendChatMessageStream(
  message: string,
  onChunk: (content: string) => void,
  image?: string,
  sessionId?: string,
  onError?: (error: string) => void,
  onDone?: () => void,
  signal?: AbortSignal,
  onReasoning?: (reasoning: string) => void,
  onReasoningEnd?: (reasoning: string) => void
): Promise<string> {
  // 使用 fetch 实现流式读取
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      image,
      session_id: sessionId || undefined
    }),
    signal  // Pass the AbortSignal to enable cancellation
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  let fullContent = ''

  if (!reader) {
    throw new Error('No reader available')
  }

  while (true) {
    const { done, value } = await reader.read()

    if (done) {
      break
    }

    const chunk = decoder.decode(value, { stream: true })
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))

          if (data.type === 'session_id') {
            // Session ID received, could be stored if needed
          } else if (data.type === 'reasoning') {
            // 思考内容
            onReasoning?.(data.reasoning)
          } else if (data.type === 'reasoning_end') {
            // 思考结束
            onReasoningEnd?.(data.reasoning)
          } else if (data.type === 'content') {
            fullContent += data.content
            onChunk(data.content)
          } else if (data.type === 'error') {
            onError?.(data.error)
            return fullContent
          } else if (data.type === 'done') {
            onDone?.()
          }
        } catch (e) {
          // Ignore parse errors for incomplete JSON
        }
      }
    }
  }

  return fullContent
}

export async function clearChat(sessionId?: string): Promise<void> {
  await axios.post(`${API_BASE}/api/chat/clear`, {
    session_id: sessionId || undefined
  }, {
    headers: {}
  })
}
