import axios from 'axios';
import type {
  User,
  LoginRequest,
  LoginResponse,
  CreateUserRequest,
  Device,
  Kiosk,
  CreateKioskRequest,
  KioskConfigData,
  AuditLog,
  DashboardStats,
  HRCode,
  CreateHRCodeRequest,
  HRCodeQRData,
} from '@/types';

// Determine API base URL.
// - In development we rely on the Vite proxy (`/api`).
// - In production builds (served from the backend) we call the API on the same origin
//   unless an explicit `VITE_API_URL` is provided.
const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL || (import.meta.env.DEV ? '/api' : ''),
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any)['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// ---------- Auth API ----------
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const form = new URLSearchParams();
    form.append('username', credentials.username);
    form.append('password', credentials.password);
    const res = await api.post<LoginResponse>('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

// ---------- Users API ----------
export const usersAPI = {
  getAll: async (params?: { offset?: number; limit?: number }): Promise<User[]> => {
    const res = await api.get<User[]>('/admin/users', { params });
    return res.data;
  },
  create: async (data: CreateUserRequest): Promise<User> => {
    const res = await api.post<User>('/admin/users', data);
    return res.data;
  },
  updateRole: async (userId: number, role: 'user' | 'admin'): Promise<void> => {
    await api.patch(`/admin/users/${userId}/role`, { role });
  },
  delete: async (userId: number): Promise<void> => {
    await api.delete(`/admin/users/${userId}`);
  },
};

// ---------- Devices API ----------
export const devicesAPI = {
  getAll: async (params?: {
    user_id?: number;
    is_revoked?: boolean;
    offset?: number;
    limit?: number;
  }): Promise<Device[]> => {
    const res = await api.get<Device[]>('/admin/devices', { params });
    return res.data;
  },
  revoke: async (deviceId: number): Promise<void> => {
    await api.post(`/admin/devices/${deviceId}/revoke`, {});
  },
};

// ---------- Kiosks API ----------
export const kiosksAPI = {
  getAll: async (params?: { is_active?: boolean; offset?: number; limit?: number }): Promise<Kiosk[]> => {
    const res = await api.get<Kiosk[]>('/admin/kiosks', { params });
    return res.data;
  },
  create: async (data: CreateKioskRequest): Promise<Kiosk> => {
    const res = await api.post<Kiosk>('/admin/kiosks', data);
    return res.data;
  },
  update: async (
    kioskId: number,
    data: Partial<Pick<Kiosk, 'kiosk_name' | 'location' | 'is_active'>>,
  ): Promise<Kiosk> => {
    const res = await api.patch<Kiosk>(`/admin/kiosks/${kioskId}`, data);
    return res.data;
  },
  delete: async (kioskId: number): Promise<void> => {
    await api.delete(`/admin/kiosks/${kioskId}`);
  },
  generateApiKey: async (kioskId: number): Promise<KioskConfigData> => {
    const res = await api.post<KioskConfigData>(`/admin/kiosks/${kioskId}/generate-api-key`, {});
    return res.data;
  },
};

// ---------- Audit Logs API ----------
export const auditLogsAPI = {
  getAll: async (params?: {
    event_type?: string;
    user_id?: number;
    device_id?: number;
    kiosk_id?: number;
    from?: string;
    to?: string;
    offset?: number;
    limit?: number;
  }): Promise<AuditLog[]> => {
    const res = await api.get<AuditLog[]>('/admin/audit-logs', { params });
    return res.data;
  },
};

// ---------- Dashboard API ----------
export const dashboardAPI = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get<DashboardStats>('/admin/dashboard/stats');
    return res.data;
  },
};

// ---------- Reports API (endpoint may be pending on backend) ----------
export const reportsAPI = {
  getAttendance: async (params: {
    from: string;
    to: string;
    user_id?: number;
    format?: 'json' | 'csv' | 'pdf';
  }): Promise<unknown | Blob> => {
    // If CSV/PDF requested, expect a blob
    if (params.format && params.format !== 'json') {
      const res = await api.get('/admin/reports/attendance', {
        params,
        responseType: 'blob',
      });
      return res.data as Blob;
    }
    const res = await api.get('/admin/reports/attendance', { params });
    return res.data;
  },
};

// ---------- HR Codes API ----------
export const hrCodesAPI = {
  getAll: async (params?: {
    include_used?: boolean;
    include_expired?: boolean;
    offset?: number;
    limit?: number;
  }): Promise<HRCode[]> => {
    const res = await api.get<HRCode[]>('/admin/hr-codes', { params });
    return res.data;
  },
  create: async (data: CreateHRCodeRequest): Promise<HRCode> => {
    const res = await api.post<HRCode>('/admin/hr-codes', data);
    return res.data;
  },
  getQRData: async (hrCodeId: number): Promise<HRCodeQRData> => {
    const res = await api.get<HRCodeQRData>(`/admin/hr-codes/${hrCodeId}/qr-data`);
    return res.data;
  },
};

export default api;

