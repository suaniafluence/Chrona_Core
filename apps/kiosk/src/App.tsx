import { useState, useEffect } from 'react'
import './App.css'
import QRScanner from './components/QRScanner'
import CameraTest from './components/CameraTest'
import ValidationResult from './components/ValidationResult'
import KioskMode from './components/KioskMode'
import ConnectionStatus from './components/ConnectionStatus'
import { getClientIp, getKioskByIp, setKioskId, KioskInfo } from './services/api'

interface PunchResult {
  success: boolean
  message: string
  punch_id?: number
  punched_at?: string
  user_id?: number
}

function App() {
  const [result, setResult] = useState<PunchResult | null>(null)
  const [isScanning, setIsScanning] = useState(true)
  const [isKioskMode, setIsKioskMode] = useState(false)
  const [showCameraTest, setShowCameraTest] = useState(false)
  const [kioskInfo, setKioskInfo] = useState<KioskInfo | null>(null)
  const [initError, setInitError] = useState<string | null>(null)
  const [isInitializing, setIsInitializing] = useState(true)

  // Initialize kiosk info from IP or environment
  useEffect(() => {
    const initializeKiosk = async () => {
      try {
        setIsInitializing(true)
        
        // Try to get IP and fetch kiosk info
        const clientIp = await getClientIp()
        
        if (clientIp) {
          try {
            const kiosk = await getKioskByIp(clientIp)
            setKioskInfo(kiosk)
            setKioskId(kiosk.id)
            console.log(`Kiosk identified by IP ${clientIp}: ${kiosk.kiosk_name}`)
          } catch (ipError) {
            console.warn(`Failed to get kiosk by IP ${clientIp}, falling back to environment variables:`, ipError)
            
            // Fallback: use environment variable
            const envKioskId = import.meta.env.VITE_KIOSK_ID
            if (envKioskId) {
              setKioskId(parseInt(envKioskId, 10))
              // Create a minimal kiosk info object from env
              setKioskInfo({
                id: parseInt(envKioskId, 10),
                kiosk_name: `Kiosk ${envKioskId}`,
                location: 'Office Entrance',
                device_fingerprint: '',
                ip_address: null,
                public_key: null,
                is_active: true,
                created_at: new Date().toISOString(),
                last_heartbeat_at: null,
              })
            } else {
              setInitError('Could not identify kiosk. Please configure VITE_KIOSK_ID in .env')
            }
          }
        } else {
          // No IP detected, fall back to environment variable
          const envKioskId = import.meta.env.VITE_KIOSK_ID
          if (envKioskId) {
            setKioskId(parseInt(envKioskId, 10))
            setKioskInfo({
              id: parseInt(envKioskId, 10),
              kiosk_name: `Kiosk ${envKioskId}`,
              location: 'Office Entrance',
              device_fingerprint: '',
              ip_address: null,
              public_key: null,
              is_active: true,
              created_at: new Date().toISOString(),
              last_heartbeat_at: null,
            })
          } else {
            setInitError('Could not identify kiosk. Please configure VITE_KIOSK_ID in .env')
          }
        }
      } catch (error) {
        console.error('Error initializing kiosk:', error)
        setInitError(`Initialization error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      } finally {
        setIsInitializing(false)
      }
    }

    initializeKiosk()
  }, [])

  const handleScanSuccess = (validationResult: PunchResult) => {
    setResult(validationResult)
    setIsScanning(false)

    // Reset after 3 seconds
    setTimeout(() => {
      setResult(null)
      setIsScanning(true)
    }, 3000)
  }

  const handleScanError = (error: string) => {
    setResult({
      success: false,
      message: error
    })
    setIsScanning(false)

    // Reset after 3 seconds
    setTimeout(() => {
      setResult(null)
      setIsScanning(true)
    }, 3000)
  }

  // Show initialization error if present
  if (initError) {
    return (
      <div className="app">
        <div style={{ position: 'fixed', top: 8, right: 8, zIndex: 1000 }}>
          <ConnectionStatus />
        </div>
        <header className="app-header">
          <h1>Chrona Kiosk - Configuration Error</h1>
          <p style={{ color: 'red' }}>{initError}</p>
          <p>Please contact administrator to configure this kiosk.</p>
        </header>
      </div>
    )
  }

  // Show loading state during initialization
  if (isInitializing || !kioskInfo) {
    return (
      <div className="app">
        <div style={{ position: 'fixed', top: 8, right: 8, zIndex: 1000 }}>
          <ConnectionStatus />
        </div>
        <header className="app-header">
          <h1>Chrona Kiosk</h1>
          <p>Initializing kiosk...</p>
          <div style={{ marginTop: 20, fontSize: 14 }}>
            <ConnectionStatus />
          </div>
        </header>
      </div>
    )
  }

  return (
    <div className={`app ${isKioskMode ? 'kiosk-mode-active' : ''}`}>
      {/* Always show connection status for visibility in E2E */}
      <div style={{ position: 'fixed', top: 8, right: 8, zIndex: 1000 }}>
        <ConnectionStatus />
      </div>
      {/* Kiosk mode controls */}
      <KioskMode
        isActive={isKioskMode}
        onToggle={() => setIsKioskMode(!isKioskMode)}
        kioskName={kioskInfo.kiosk_name}
        location={kioskInfo.location}
      />

      {!isKioskMode && (
        <header className="app-header">
          <h1>Chrona Kiosk</h1>
          <p>Scanner le QR code pour pointer</p>
          <div style={{ marginTop: 8 }}>
            <ConnectionStatus />
          </div>
        </header>
      )}

      <main className="app-main">
        <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
          <button
            className={`btn ${!showCameraTest ? 'btn--active' : ''}`}
            onClick={() => setShowCameraTest(false)}
            disabled={!showCameraTest}
          >
            Mode scan QR
          </button>
          <button
            className={`btn ${showCameraTest ? 'btn--active' : ''}`}
            onClick={() => setShowCameraTest(true)}
            disabled={showCameraTest}
          >
            Mode test camera
          </button>
        </div>
        {showCameraTest ? (
          <CameraTest />
        ) : isScanning ? (
          <QRScanner onScanSuccess={handleScanSuccess} onScanError={handleScanError} />
        ) : (
          <ValidationResult result={result} />
        )}
      </main>

      <footer className="app-footer">
        <p>Copyright 2025 Chrona - Systeme de pointage securise</p>
      </footer>
    </div>
  )
}

export default App
