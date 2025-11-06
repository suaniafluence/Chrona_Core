export interface User {
  id: number;
  email: string;
  role: 'user' | 'admin';
  created_at: string;
}

export interface Device {
  id: number;
  user_id: number;
  device_fingerprint: string;
  device_name: string;
  registered_at: string;
  last_seen_at: string;
  is_revoked: boolean;
}

export interface Kiosk {
  id: number;
  kiosk_name: string;
  location: string;
  device_fingerprint: string;
  is_active: boolean;
  created_at: string;
  last_heartbeat_at?: string | null;
  api_key?: string;
}

export interface Punch {
  id: number;
  user_id: number;
  device_id: number;
  kiosk_id: number;
  punch_type: 'clock_in' | 'clock_out';
  punched_at: string;
  jwt_jti: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  event_type: string;
  user_id: number | null;
  device_id: number | null;
  kiosk_id: number | null;
  event_data: Record<string, unknown>;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_users: number;
  total_devices: number;
  total_kiosks: number;
  active_kiosks: number;
  today_punches: number;
  today_users: number;
  recent_punches: Punch[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  role: 'user' | 'admin';
}

export interface CreateKioskRequest {
  kiosk_name: string;
  location: string;
  device_fingerprint?: string;
}

export interface KioskConfigData {
  kiosk_id: number;
  kiosk_name: string;
  location: string;
  api_url: string;
  api_key: string;
  device_fingerprint: string;
}

export interface CreateKioskResponse extends Kiosk {
  api_key: string;
}

export interface HRCode {
  id: number;
  code: string;
  employee_email: string;
  employee_name: string | null;
  created_by_admin_id: number | null;
  created_at: string;
  expires_at: string | null;
  is_used: boolean;
  used_at: string | null;
  used_by_user_id: number | null;
}

export interface CreateHRCodeRequest {
  employee_email: string;
  employee_name?: string;
  expires_in_days?: number;
}

export interface HRCodeQRData {
  api_url: string;
  hr_code: string;
  employee_email: string;
  employee_name: string | null;
}

export interface CreateDeviceRequest {
  device_fingerprint: string;
  device_name: string;
  attestation_data?: Record<string, unknown> | null;
}

export interface QRCodeToken {
  qr_token: string;
  expires_in: number;
  expires_at: string;
}
