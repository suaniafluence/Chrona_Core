import { useState } from 'react'
import './App.css'
import QRScanner from './components/QRScanner'
import ValidationResult from './components/ValidationResult'
import KioskControls from './components/KioskControls'
import { useKioskMode } from './hooks/useKioskMode'

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

  // Kiosk mode management
  const {
    isKioskMode,
    isFullscreen,
    enterKioskMode,
    exitKioskMode,
    toggleFullscreen,
    showExitButton,
  } = useKioskMode()

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
      {/* Kiosk mode controls */}
      <KioskControls
        isKioskMode={isKioskMode}
        isFullscreen={isFullscreen}
        showExitButton={showExitButton}
        onEnterKioskMode={enterKioskMode}
        onExitKioskMode={exitKioskMode}
        onToggleFullscreen={toggleFullscreen}
      />

      <header className="app-header">
        <h1>Chrona Kiosk</h1>
        <p>Scanner le QR code pour pointer</p>
      </header>

      <main className="app-main">
        {isScanning ? (
          <QRScanner
            onScanSuccess={handleScanSuccess}
            onScanError={handleScanError}
          />
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
