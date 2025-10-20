/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_KIOSK_ID: string
  readonly VITE_PUNCH_TYPE: 'clock_in' | 'clock_out'
  readonly VITE_KIOSK_API_KEY: string
  readonly VITE_AUTO_KIOSK_MODE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
