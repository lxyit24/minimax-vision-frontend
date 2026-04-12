import axios from 'axios'

// Direct backend URL to bypass Vite proxy issues
const API_BASE = 'http://localhost:5001'

export async function analyzeImage(file: File, prompt?: string): Promise<string> {
  const formData = new FormData()
  formData.append('image', file)
  if (prompt) {
    formData.append('prompt', prompt)
  }
  
  const response = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 120000 // 2 minutes timeout for image analysis
  })
  
  return response.data.result
}
