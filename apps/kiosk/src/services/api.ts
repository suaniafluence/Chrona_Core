import axios from 'axios'

// Get API key from environment or localStorage
const getApiKey = (): string => {
  const apiKey = localStorage.getItem('kioskApiKey') || import.meta.env.VITE_KIOSK_API_KEY
  if (!apiKey || apiKey === 'your-api-key-here') {
    console.error('Kiosk API key not configured. Please set VITE_KIOSK_API_KEY or configure in localStorage.')
    throw new Error('Kiosk API key not configured')
  }
  return apiKey
}

// Use the Vite proxy: /api will be rewritten to the backend URL
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add API key to all requests
api.interceptors.request.use((config) => {
  try {
    const apiKey = getApiKey()
    config.headers['X-Kiosk-API-Key'] = apiKey
  } catch (error) {
    console.error('Failed to get API key:', error)
  }
  return config
})

// Get kiosk ID from environment or localStorage
const getKioskId = (): number => {
  const kioskId = localStorage.getItem('kioskId') || import.meta.env.VITE_KIOSK_ID
  if (!kioskId) {
    throw new Error('Kiosk ID not configured. Please set VITE_KIOSK_ID or configure in localStorage.')
  }
  return parseInt(kioskId, 10)
}

// Get punch type from environment or default to clock_in
const getPunchType = (): 'clock_in' | 'clock_out' => {
  const punchType = localStorage.getItem('punchType') || import.meta.env.VITE_PUNCH_TYPE || 'clock_in'
  return punchType as 'clock_in' | 'clock_out'
}

export interface PunchValidateRequest {
  qr_token: string
  kiosk_id: number
  punch_type: 'clock_in' | 'clock_out'
}

export interface PunchValidateResponse {
  success: boolean
  message: string
  punch_id?: number
  punched_at?: string
  user_id?: number
  device_id?: number
}

/**
 * Validate a punch by sending the QR token to the backend
 */
export const validatePunch = async (qrToken: string): Promise<PunchValidateResponse> => {
  const request: PunchValidateRequest = {
    qr_token: qrToken,
    kiosk_id: getKioskId(),
    punch_type: getPunchType(),
  }

  const response = await api.post<PunchValidateResponse>('/punch/validate', request)
  return response.data
}

/**
 * Health check to verify backend connectivity
 */
export const healthCheck = async (): Promise<{ status: string; db: string }> => {
  const response = await api.get('/health')
  return response.data
}

export default api
