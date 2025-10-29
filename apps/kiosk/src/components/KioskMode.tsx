import { useState, useEffect } from 'react'
import './KioskMode.css'
import ConnectionStatus from './ConnectionStatus'

interface KioskModeProps {
  isActive: boolean
  onToggle: () => void
  kioskName?: string
  location?: string
}

export default function KioskMode({ isActive, onToggle, kioskName, location }: KioskModeProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showExitPrompt, setShowExitPrompt] = useState(false)

  useEffect(() => {
    // Check if already in fullscreen
    const checkFullscreen = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', checkFullscreen)
    return () => document.removeEventListener('fullscreenchange', checkFullscreen)
  }, [])

  useEffect(() => {
    // Auto-enter kiosk mode if configured
    const autoKioskMode = import.meta.env.VITE_AUTO_KIOSK_MODE === 'true'
    if (autoKioskMode && !isActive) {
      handleEnterKioskMode()
    }
  }, [])

  const handleEnterKioskMode = async () => {
    try {
      // Request fullscreen
      await document.documentElement.requestFullscreen()
      onToggle()
    } catch (err) {
      console.error('Failed to enter fullscreen:', err)
    }
  }

  const handleExitKioskMode = async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen()
      }
      onToggle()
      setShowExitPrompt(false)
    } catch (err) {
      console.error('Failed to exit fullscreen:', err)
    }
  }

  const handleExitRequest = () => {
    setShowExitPrompt(true)
  }

  if (!isActive) {
    return (
      <div className="kiosk-mode-prompt" data-testid="kiosk-mode-prompt">
        <button
          onClick={handleEnterKioskMode}
          className="kiosk-mode-btn"
          data-testid="kiosk-mode-toggle"
        >
          Enter Kiosk Mode
        </button>
      </div>
    )
  }

  return (
    <>
      {/* Kiosk Header */}
      <div className="kiosk-header" data-testid="kiosk-header">
        <div className="kiosk-info" data-testid="kiosk-info">
          <h2>{kioskName || 'Chrona Kiosk'}</h2>
          {location && <p className="kiosk-location">{location}</p>}
        </div>
        <div className="kiosk-header-actions">
          <ConnectionStatus />
          <button
            onClick={handleExitRequest}
            className="exit-kiosk-btn"
            title="Exit Kiosk Mode"
            data-testid="exit-kiosk-btn"
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* Exit Confirmation Dialog */}
      {showExitPrompt && (
        <div className="exit-prompt-overlay" data-testid="exit-prompt">
          <div className="exit-prompt">
            <h3>Exit Kiosk Mode?</h3>
            <p>This will exit fullscreen and return to normal mode.</p>
            <div className="exit-prompt-actions">
              <button
                onClick={handleExitKioskMode}
                className="btn-confirm"
                data-testid="confirm-exit"
              >
                Exit
              </button>
              <button
                onClick={() => setShowExitPrompt(false)}
                className="btn-cancel"
                data-testid="cancel-exit"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
