import axios from 'axios'

// Get API key from environment or localStorage
const getApiKey = (): string => {
  const apiKey = localStorage.getItem('kioskApiKey') || import.meta.env.VITE_KIOSK_API_KEY
  if (!apiKey || apiKey === 'your-api-key-here') {
    // Log warning but don't throw - allow page to load without API key
    // (useful for development/testing before E2E setup)
    if (import.meta.env.DEV) {
      console.warn('Kiosk API key not configured. Please set VITE_KIOSK_API_KEY in .env or configure in localStorage.')
    }
    return ''  // Return empty string instead of throwing
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

// Add API key to all requests (if available)
api.interceptors.request.use((config) => {
  try {
    const apiKey = getApiKey()
    if (apiKey) {
      config.headers['X-Kiosk-API-Key'] = apiKey
    }
  } catch (error) {
    console.error('Failed to get API key:', error)
  }
  return config
})

// Detect client IP address
export const getClientIp = async (): Promise<string | null> => {
  try {
    // Try getting IP from a public IP detection service
    // For local networks, this may return the external IP
    // So we try multiple methods
    
    // Method 1: Try using whatismyip API (requires internet)
    try {
      const response = await fetch('https://api.ipify.org?format=json', { 
        mode: 'no-cors',
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      })
      if (response.ok) {
        const data = await response.json()
        return data.ip
      }
    } catch (e) {
      console.debug('Could not detect IP from ipify:', e)
    }

    // Method 2: Try a simple IP detection endpoint
    try {
      const response = await axios.get('/api/info/ip', { timeout: 2000 })
      if (response.data && response.data.ip) {
        return response.data.ip
      }
    } catch (e) {
      console.debug('Could not detect IP from backend:', e)
    }

    // Method 3: Use localhost as fallback for development
    if (import.meta.env.DEV) {
      console.debug('Could not auto-detect IP, using localhost fallback')
      return 'localhost'
    }

    return null
  } catch (error) {
    console.error('Error detecting client IP:', error)
    return null
  }
}

// Get kiosk info by IP address
export interface KioskInfo {
  id: number
  kiosk_name: string
  location: string
  device_fingerprint: string
  ip_address: string | null
  public_key: string | null
  is_active: boolean
  created_at: string
  last_heartbeat_at: string | null
}

export const getKioskByIp = async (ipAddress: string): Promise<KioskInfo> => {
  try {
    const response = await api.get<KioskInfo>(`/admin/kiosks/by-ip/${ipAddress}`)
    return response.data
  } catch (error) {
    console.error(`Failed to get kiosk info for IP ${ipAddress}:`, error)
    throw error
  }
}

// Get kiosk ID from environment, localStorage, or auto-detect
let cachedKioskId: number | null = null

const getKioskId = (): number => {
  // Check cache first
  if (cachedKioskId !== null) {
    return cachedKioskId
  }

  // Try localStorage
  const stored = localStorage.getItem('kioskId')
  if (stored) {
    cachedKioskId = parseInt(stored, 10)
    return cachedKioskId
  }

  // Try environment variable (legacy)
  const envId = import.meta.env.VITE_KIOSK_ID
  if (envId) {
    cachedKioskId = parseInt(envId, 10)
    return cachedKioskId
  }

  // Default fallback (should not reach here after Phase 3b initialization)
  if (import.meta.env.DEV) {
    console.warn('Kiosk ID not configured. Will be set during app initialization.')
  }
  return 1  // Default fallback
}

// Set kiosk ID (called during app initialization)
export const setKioskId = (id: number): void => {
  cachedKioskId = id
  localStorage.setItem('kioskId', String(id))
}

// Get punch type from environment or default to clock_in
const getPunchType = (): 'clock_in' | 'clock_out' => {
  const punchType = localStorage.getItem('punchType') || import.meta.env.VITE_PUNCH_TYPE || 'clock_in'
  return punchType as 'clock_in' | 'clock_out'
}

export interface PunchValidateRequest {
  qr_token: string
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
 * Note: kiosk_id is no longer needed - server identifies kiosk by client IP
 */
export const validatePunch = async (qrToken: string): Promise<PunchValidateResponse> => {
  const request: PunchValidateRequest = {
    qr_token: qrToken,
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
