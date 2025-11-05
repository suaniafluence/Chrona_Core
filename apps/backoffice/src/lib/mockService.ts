import type {
  User,
  Device,
  Kiosk,
  AuditLog,
  DashboardStats,
  HRCode,
  CreateUserRequest,
  CreateKioskRequest,
  CreateHRCodeRequest,
  CreateDeviceRequest,
  QRCodeToken,
} from '@/types';
import {
  mockUsers,
  mockDevices,
  mockKiosks,
  mockPunches,
  mockAuditLogs,
  mockHRCodes,
} from './mockData';

// Simple in-memory storage for created items during development
let users = [...mockUsers];
let devices = [...mockDevices];
let kiosks = [...mockKiosks];
let punches = [...mockPunches];
let auditLogs = [...mockAuditLogs];
let hrCodes = [...mockHRCodes];

// Helper to get next ID
const getNextId = <T extends { id: number }>(items: T[]): number => {
  return Math.max(...items.map(i => i.id), 0) + 1;
};

// Simulate network delay
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms));

export const mockService = {
  // Users
  getUsers: async (): Promise<User[]> => {
    await delay();
    return users;
  },
  createUser: async (data: CreateUserRequest): Promise<User> => {
    await delay();
    const user: User = {
      id: getNextId(users),
      ...data,
      created_at: new Date().toISOString(),
    };
    users.push(user);
    return user;
  },
  updateUserRole: async (userId: number, role: 'user' | 'admin'): Promise<void> => {
    await delay();
    const user = users.find(u => u.id === userId);
    if (user) {
      user.role = role;
    }
  },
  deleteUser: async (userId: number): Promise<void> => {
    await delay();
    users = users.filter(u => u.id !== userId);
    // Also remove associated devices
    devices = devices.filter(d => d.user_id !== userId);
  },

  // Devices
  getDevices: async (filters?: {
    user_id?: number;
    is_revoked?: boolean;
  }): Promise<Device[]> => {
    await delay();
    let result = devices;
    if (filters?.user_id !== undefined) {
      result = result.filter(d => d.user_id === filters.user_id);
    }
    if (filters?.is_revoked !== undefined) {
      result = result.filter(d => d.is_revoked === filters.is_revoked);
    }
    return result;
  },
  createDevice: async (data: CreateDeviceRequest): Promise<Device> => {
    await delay();
    // Get current user ID from context (mock assumes user 1)
    const userId = 1; // In real app, this would come from auth context
    const device: Device = {
      id: getNextId(devices),
      user_id: userId,
      device_fingerprint: data.device_fingerprint,
      device_name: data.device_name,
      registered_at: new Date().toISOString(),
      last_seen_at: new Date().toISOString(),
      is_revoked: false,
    };
    devices.push(device);
    return device;
  },
  revokeDevice: async (deviceId: number): Promise<void> => {
    await delay();
    const device = devices.find(d => d.id === deviceId);
    if (device) {
      device.is_revoked = true;
    }
  },
  generateQRToken: async (deviceId: number): Promise<QRCodeToken> => {
    await delay();
    const device = devices.find(d => d.id === deviceId);
    if (!device) throw new Error('Device not found');

    // Generate mock JWT token (in real app, backend does this)
    const expiresIn = 30;
    const expiresAt = new Date(Date.now() + expiresIn * 1000).toISOString();
    const mockToken = `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZGV2aWNlX2lkIjogJHtMZXZpY2VJZH0sIm5vbmNlIjogImR1bW15Tm9uY2UiLCJqdGkiOiAiZHVtbXlKdGkiLCJleHAiOiAke01hdGguZmxvb3IoRGF0ZS5ub3coKSAvIDEwMDApICsgMzB9fQ.${Date.now()}`;

    return {
      qr_token: mockToken,
      expires_in: expiresIn,
      expires_at: expiresAt,
    };
  },

  // Kiosks
  getKiosks: async (filters?: {
    is_active?: boolean;
  }): Promise<Kiosk[]> => {
    await delay();
    let result = kiosks;
    if (filters?.is_active !== undefined) {
      result = result.filter(k => k.is_active === filters.is_active);
    }
    return result;
  },
  createKiosk: async (data: CreateKioskRequest): Promise<Kiosk> => {
    await delay();
    const kiosk: Kiosk = {
      id: getNextId(kiosks),
      ...data,
      is_active: true,
      created_at: new Date().toISOString(),
      device_fingerprint: data.device_fingerprint || `kiosk_fp_${Date.now()}`,
    };
    kiosks.push(kiosk);
    return kiosk;
  },
  updateKiosk: async (
    kioskId: number,
    data: Partial<Pick<Kiosk, 'kiosk_name' | 'location' | 'is_active'>>
  ): Promise<Kiosk> => {
    await delay();
    const kiosk = kiosks.find(k => k.id === kioskId);
    if (!kiosk) throw new Error('Kiosk not found');
    Object.assign(kiosk, data);
    return kiosk;
  },
  deleteKiosk: async (kioskId: number): Promise<void> => {
    await delay();
    kiosks = kiosks.filter(k => k.id !== kioskId);
  },

  // Audit Logs
  getAuditLogs: async (filters?: {
    event_type?: string;
    user_id?: number;
  }): Promise<AuditLog[]> => {
    await delay();
    let result = auditLogs;
    if (filters?.event_type) {
      result = result.filter(log => log.event_type === filters.event_type);
    }
    if (filters?.user_id) {
      result = result.filter(log => log.user_id === filters.user_id);
    }
    return result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  },

  // Dashboard Stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    await delay();
    return {
      total_users: users.length,
      total_devices: devices.filter(d => !d.is_revoked).length,
      total_kiosks: kiosks.length,
      active_kiosks: kiosks.filter(k => k.is_active).length,
      today_punches: punches.filter(p => {
        const today = new Date();
        const punchDate = new Date(p.punched_at);
        return punchDate.toDateString() === today.toDateString();
      }).length,
      today_users: new Set(
        punches
          .filter(p => {
            const today = new Date();
            const punchDate = new Date(p.punched_at);
            return punchDate.toDateString() === today.toDateString();
          })
          .map(p => p.user_id)
      ).size,
      recent_punches: punches.slice(0, 10),
    };
  },

  // HR Codes
  getHRCodes: async (filters?: {
    include_used?: boolean;
    include_expired?: boolean;
  }): Promise<HRCode[]> => {
    await delay();
    let result = hrCodes;
    if (!filters?.include_used) {
      result = result.filter(code => !code.is_used);
    }
    if (!filters?.include_expired) {
      const now = new Date();
      result = result.filter(code => !code.expires_at || new Date(code.expires_at) > now);
    }
    return result;
  },
  createHRCode: async (data: CreateHRCodeRequest): Promise<HRCode> => {
    await delay();
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + (data.expires_in_days || 30));

    const hrCode: HRCode = {
      id: getNextId(hrCodes),
      code: `HR-${Date.now()}`,
      employee_email: data.employee_email,
      employee_name: data.employee_name || null,
      created_by_admin_id: 1, // Mock current admin ID
      created_at: new Date().toISOString(),
      expires_at: expiresAt.toISOString(),
      is_used: false,
      used_at: null,
      used_by_user_id: null,
    };
    hrCodes.push(hrCode);
    return hrCode;
  },

  // Reset data to initial state
  resetData: () => {
    users = [...mockUsers];
    devices = [...mockDevices];
    kiosks = [...mockKiosks];
    punches = [...mockPunches];
    auditLogs = [...mockAuditLogs];
    hrCodes = [...mockHRCodes];
  },
};

// Enable mock service in development mode
export const isMockServiceEnabled = (): boolean => {
  return import.meta.env.DEV && localStorage.getItem('USE_MOCK_API') === 'true';
};

// Toggle mock service
export const toggleMockService = (enabled: boolean) => {
  if (enabled) {
    localStorage.setItem('USE_MOCK_API', 'true');
    console.log('✅ Mock API service enabled');
  } else {
    localStorage.removeItem('USE_MOCK_API');
    console.log('❌ Mock API service disabled');
  }
};
