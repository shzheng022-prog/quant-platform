// API配置
const isProduction = import.meta.env.PROD
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export const apiClient = {
  baseURL: API_BASE_URL,
  
  async get(endpoint, params = {}) {
    const url = new URL(endpoint, isProduction ? API_BASE_URL : '/api')
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
    
    const response = await fetch(url.toString())
    return response.json()
  },
  
  async post(endpoint, data = {}) {
    const url = isProduction ? `${API_BASE_URL}${endpoint}` : `/api${endpoint}`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    return response.json()
  }
}
