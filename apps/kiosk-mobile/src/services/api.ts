import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Storage keys
const STORAGE_KEYS = {
  API_BASE_URL: '@chrona_kiosk_api_base_url',
  KIOSK_ID: '@chrona_kiosk_id',
  KIOSK_API_KEY: '@chrona_kiosk_api_key',
  PUNCH_TYPE: '@chrona_kiosk_punch_type',
};

// Default configuration
const DEFAULT_CONFIG = {
  API_BASE_URL: 'http://192.168.1.100:8000', // Remplacer par l'IP du serveur
  KIOSK_ID: '1',
  PUNCH_TYPE: 'clock_in' as 'clock_in' | 'clock_out',
};

/**
 * Configuration manager for kiosk settings
 */
export class KioskConfig {
  private static instance: KioskConfig;
  private config: {
    apiBaseUrl: string;
    kioskId: number;
    kioskApiKey: string;
    punchType: 'clock_in' | 'clock_out';
  } = {
    apiBaseUrl: DEFAULT_CONFIG.API_BASE_URL,
    kioskId: parseInt(DEFAULT_CONFIG.KIOSK_ID, 10),
    kioskApiKey: '',
    punchType: DEFAULT_CONFIG.PUNCH_TYPE,
  };

  private constructor() {}

  static getInstance(): KioskConfig {
    if (!KioskConfig.instance) {
      KioskConfig.instance = new KioskConfig();
    }
    return KioskConfig.instance;
  }

  /**
   * Load configuration from AsyncStorage
   */
  async loadConfig(): Promise<void> {
    try {
      const [apiBaseUrl, kioskId, kioskApiKey, punchType] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.API_BASE_URL),
        AsyncStorage.getItem(STORAGE_KEYS.KIOSK_ID),
        AsyncStorage.getItem(STORAGE_KEYS.KIOSK_API_KEY),
        AsyncStorage.getItem(STORAGE_KEYS.PUNCH_TYPE),
      ]);

      if (apiBaseUrl) this.config.apiBaseUrl = apiBaseUrl;
      if (kioskId) this.config.kioskId = parseInt(kioskId, 10);
      if (kioskApiKey) this.config.kioskApiKey = kioskApiKey;
      if (punchType) this.config.punchType = punchType as 'clock_in' | 'clock_out';

      console.log('Kiosk config loaded:', {
        apiBaseUrl: this.config.apiBaseUrl,
        kioskId: this.config.kioskId,
        punchType: this.config.punchType,
      });
    } catch (error) {
      console.error('Failed to load kiosk config:', error);
    }
  }

  /**
   * Save configuration to AsyncStorage
   */
  async saveConfig(updates: Partial<typeof this.config>): Promise<void> {
    try {
      const promises: Promise<void>[] = [];

      if (updates.apiBaseUrl !== undefined) {
        this.config.apiBaseUrl = updates.apiBaseUrl;
        promises.push(AsyncStorage.setItem(STORAGE_KEYS.API_BASE_URL, updates.apiBaseUrl));
      }

      if (updates.kioskId !== undefined) {
        this.config.kioskId = updates.kioskId;
        promises.push(AsyncStorage.setItem(STORAGE_KEYS.KIOSK_ID, updates.kioskId.toString()));
      }

      if (updates.kioskApiKey !== undefined) {
        this.config.kioskApiKey = updates.kioskApiKey;
        promises.push(AsyncStorage.setItem(STORAGE_KEYS.KIOSK_API_KEY, updates.kioskApiKey));
      }

      if (updates.punchType !== undefined) {
        this.config.punchType = updates.punchType;
        promises.push(AsyncStorage.setItem(STORAGE_KEYS.PUNCH_TYPE, updates.punchType));
      }

      await Promise.all(promises);
      console.log('Kiosk config saved:', this.config);
    } catch (error) {
      console.error('Failed to save kiosk config:', error);
      throw error;
    }
  }

  getApiBaseUrl(): string {
    return this.config.apiBaseUrl;
  }

  getKioskId(): number {
    return this.config.kioskId;
  }

  getKioskApiKey(): string {
    return this.config.kioskApiKey;
  }

  getPunchType(): 'clock_in' | 'clock_out' {
    return this.config.punchType;
  }

  getConfig() {
    return { ...this.config };
  }
}

/**
 * Create axios instance for API calls
 */
export class ApiService {
  private static instance: ApiService;
  private axiosInstance: AxiosInstance;
  private config: KioskConfig;

  private constructor() {
    this.config = KioskConfig.getInstance();
    this.axiosInstance = axios.create({
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to set dynamic base URL and API key
    this.axiosInstance.interceptors.request.use(
      (config) => {
        config.baseURL = this.config.getApiBaseUrl();
        const apiKey = this.config.getKioskApiKey();
        if (apiKey) {
          config.headers['X-Kiosk-API-Key'] = apiKey;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === 'ECONNABORTED') {
          console.error('Request timeout');
        } else if (error.response) {
          console.error('API error:', error.response.status, error.response.data);
        } else if (error.request) {
          console.error('Network error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  getAxios(): AxiosInstance {
    return this.axiosInstance;
  }
}

// Request/Response types
export interface PunchValidateRequest {
  qr_token: string;
  kiosk_id: number;
  punch_type: 'clock_in' | 'clock_out';
}

export interface PunchValidateResponse {
  success: boolean;
  message: string;
  punch_id?: number;
  punched_at?: string;
  user_id?: number;
  device_id?: number;
}

export interface HealthCheckResponse {
  status: string;
  db: string;
}

/**
 * API methods
 */
const api = ApiService.getInstance().getAxios();
const config = KioskConfig.getInstance();

/**
 * Validate a punch by sending the QR token to the backend
 */
export const validatePunch = async (qrToken: string): Promise<PunchValidateResponse> => {
  const request: PunchValidateRequest = {
    qr_token: qrToken,
    kiosk_id: config.getKioskId(),
    punch_type: config.getPunchType(),
  };

  const response = await api.post<PunchValidateResponse>('/punch/validate', request);
  return response.data;
};

/**
 * Health check to verify backend connectivity
 */
export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await api.get<HealthCheckResponse>('/health');
  return response.data;
};

export default api;
