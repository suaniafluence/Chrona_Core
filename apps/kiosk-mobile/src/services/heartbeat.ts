import { AppState, AppStateStatus, Platform } from 'react-native';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import api from './api';

// Heartbeat configuration
const HEARTBEAT_INTERVAL = 60000; // 60 seconds
const HEARTBEAT_ENDPOINT = '/kiosk/heartbeat';

export interface HeartbeatData {
  app_version: string;
  device_info?: string;
}

export interface HeartbeatResponse {
  success: boolean;
  message: string;
  kiosk_id: number;
  last_heartbeat_at: string;
  server_time: string;
}

/**
 * Heartbeat service to periodically ping the backend
 * and signal that the kiosk is online and functioning.
 */
export class HeartbeatService {
  private static instance: HeartbeatService;
  private intervalId: NodeJS.Timeout | null = null;
  private isRunning: boolean = false;
  private appVersion: string = '1.0.0';
  private deviceInfo: string = '';

  private constructor() {
    this.initializeDeviceInfo();
  }

  static getInstance(): HeartbeatService {
    if (!HeartbeatService.instance) {
      HeartbeatService.instance = new HeartbeatService();
    }
    return HeartbeatService.instance;
  }

  /**
   * Initialize device information
   */
  private async initializeDeviceInfo() {
    try {
      // Get app version
      this.appVersion = Application.nativeApplicationVersion || '1.0.0';

      // Get device info
      const deviceModel = Device.modelName || Device.deviceName || 'Unknown';
      const osVersion = Device.osVersion || 'Unknown';
      const platform = Platform.OS;

      this.deviceInfo = `${platform}/${osVersion} - ${deviceModel}`;
      console.log('Heartbeat: Device info initialized:', this.deviceInfo);
    } catch (error) {
      console.error('Heartbeat: Failed to initialize device info:', error);
      this.deviceInfo = `${Platform.OS}/Unknown`;
    }
  }

  /**
   * Start sending periodic heartbeats
   */
  start() {
    if (this.isRunning) {
      console.log('Heartbeat: Already running');
      return;
    }

    console.log('Heartbeat: Starting service...');
    this.isRunning = true;

    // Send initial heartbeat immediately
    this.sendHeartbeat();

    // Set up periodic heartbeat
    this.intervalId = setInterval(() => {
      this.sendHeartbeat();
    }, HEARTBEAT_INTERVAL);

    // Listen to app state changes
    AppState.addEventListener('change', this.handleAppStateChange);
  }

  /**
   * Stop sending heartbeats
   */
  stop() {
    if (!this.isRunning) {
      return;
    }

    console.log('Heartbeat: Stopping service...');
    this.isRunning = false;

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    // Remove app state listener
    AppState.removeEventListener('change', this.handleAppStateChange);
  }

  /**
   * Handle app state changes (pause/resume heartbeat)
   */
  private handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (nextAppState === 'active') {
      console.log('Heartbeat: App became active, resuming heartbeats');
      if (!this.intervalId && this.isRunning) {
        this.sendHeartbeat();
        this.intervalId = setInterval(() => {
          this.sendHeartbeat();
        }, HEARTBEAT_INTERVAL);
      }
    } else if (nextAppState === 'background' || nextAppState === 'inactive') {
      console.log('Heartbeat: App went to background, pausing heartbeats');
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    }
  };

  /**
   * Send a single heartbeat to the backend
   */
  private async sendHeartbeat() {
    if (!this.isRunning) {
      return;
    }

    try {
      const data: HeartbeatData = {
        app_version: this.appVersion,
        device_info: this.deviceInfo,
      };

      const response = await api.post<HeartbeatResponse>(
        HEARTBEAT_ENDPOINT,
        data,
        {
          timeout: 10000, // 10 second timeout
        }
      );

      console.log('Heartbeat: Sent successfully', {
        kiosk_id: response.data.kiosk_id,
        server_time: response.data.server_time,
      });
    } catch (error: any) {
      // Log error but don't crash the app
      if (error.response) {
        console.error(
          'Heartbeat: Failed with status',
          error.response.status,
          error.response.data
        );
      } else if (error.request) {
        console.error('Heartbeat: Network error, no response received');
      } else {
        console.error('Heartbeat: Error', error.message);
      }
    }
  }

  /**
   * Force send a heartbeat immediately
   */
  async sendImmediately(): Promise<boolean> {
    try {
      await this.sendHeartbeat();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get current heartbeat status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      appVersion: this.appVersion,
      deviceInfo: this.deviceInfo,
      interval: HEARTBEAT_INTERVAL,
    };
  }
}

export default HeartbeatService;
