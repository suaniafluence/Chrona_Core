import { useState } from 'react'
import './App.css'
import QRScanner from './components/QRScanner'
import CameraTest from './components/CameraTest'
import ValidationResult from './components/ValidationResult'
import KioskMode from './components/KioskMode'
import ConnectionStatus from './components/ConnectionStatus'

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

  // Get kiosk info from environment
  const kioskId = import.meta.env.VITE_KIOSK_ID
  const kioskName = `Kiosk ${kioskId}`
  const location = 'Office Entrance'

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
        kioskName={kioskName}
        location={location}
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
            Mode test caméra
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
        <p>&copy; 2025 Chrona - Système de pointage sécurisé</p>
      </footer>
    </div>
  )
}

export default App
