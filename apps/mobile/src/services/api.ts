import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuration API
const API_URL = __DEV__
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'https://api.chrona.com'; // Production

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor pour ajouter le token JWT
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('@auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface DeviceRegisterRequest {
  device_fingerprint: string;
  device_name: string;
  attestation_data?: string;
}

export interface QRTokenRequest {
  device_id: number;
}

export interface QRTokenResponse {
  qr_token: string;
  expires_in: number;
  expires_at: string;
}

export interface PunchHistoryItem {
  id: number;
  punch_type: 'clock_in' | 'clock_out';
  punched_at: string;
  kiosk_id: number;
  created_at: string;
}

// Onboarding Types (Level B)
export interface OnboardingInitiateRequest {
  hr_code: string;
  email: string;
}

export interface OnboardingInitiateResponse {
  success: boolean;
  message: string;
  session_token?: string;
  step?: string;
}

export interface OnboardingVerifyOTPRequest {
  session_token: string;
  otp_code: string;
}

export interface OnboardingVerifyOTPResponse {
  success: boolean;
  message: string;
  step?: string;
}

export interface OnboardingCompleteRequest {
  session_token: string;
  password: string;
  device_fingerprint: string;
  device_name: string;
  attestation_data?: string;
}

export interface OnboardingCompleteResponse {
  success: boolean;
  message: string;
  user_id?: number;
  device_id?: number;
  access_token?: string;
}

// API Functions
export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<LoginResponse>('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (email: string, password: string): Promise<any> => {
    const response = await api.post('/auth/register', {
      email,
      password,
    });
    return response.data;
  },
};

export const deviceService = {
  registerDevice: async (data: DeviceRegisterRequest): Promise<any> => {
    const response = await api.post('/devices/register', data);
    return response.data;
  },

  getMyDevices: async (): Promise<any[]> => {
    const response = await api.get('/devices/me');
    return response.data;
  },

  revokeDevice: async (deviceId: number): Promise<any> => {
    const response = await api.post(`/devices/${deviceId}/revoke`);
    return response.data;
  },
};

export const punchService = {
  requestQRToken: async (deviceId: number): Promise<QRTokenResponse> => {
    const response = await api.post<QRTokenResponse>('/punch/request-token', {
      device_id: deviceId,
    });
    return response.data;
  },

  getHistory: async (): Promise<PunchHistoryItem[]> => {
    const response = await api.get<PunchHistoryItem[]>('/punch/history');
    return response.data;
  },
};

export const onboardingService = {
  initiateOnboarding: async (
    hrCode: string,
    email: string
  ): Promise<OnboardingInitiateResponse> => {
    const response = await api.post<OnboardingInitiateResponse>(
      '/onboarding/initiate',
      {
        hr_code: hrCode,
        email,
      }
    );
    return response.data;
  },

  verifyOTP: async (
    sessionToken: string,
    otpCode: string
  ): Promise<OnboardingVerifyOTPResponse> => {
    const response = await api.post<OnboardingVerifyOTPResponse>(
      '/onboarding/verify-otp',
      {
        session_token: sessionToken,
        otp_code: otpCode,
      }
    );
    return response.data;
  },

  completeOnboarding: async (
    data: OnboardingCompleteRequest
  ): Promise<OnboardingCompleteResponse> => {
    const response = await api.post<OnboardingCompleteResponse>(
      '/onboarding/complete',
      data
    );
    return response.data;
  },
};

export default api;
