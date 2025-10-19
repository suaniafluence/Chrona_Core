/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_KIOSK_ID: string
  readonly VITE_PUNCH_TYPE: 'clock_in' | 'clock_out'
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
