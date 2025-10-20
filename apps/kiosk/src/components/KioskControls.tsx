/**
 * Kiosk mode controls component
 * Shows fullscreen toggle and exit kiosk mode button
 */
import './KioskControls.css'

interface KioskControlsProps {
  isKioskMode: boolean
  isFullscreen: boolean
  showExitButton: boolean
  onEnterKioskMode: () => void
  onExitKioskMode: () => void
  onToggleFullscreen: () => void
}

export default function KioskControls({
  isKioskMode,
  isFullscreen,
  showExitButton,
  onEnterKioskMode,
  onExitKioskMode,
  onToggleFullscreen,
}: KioskControlsProps) {
  if (isKioskMode && !showExitButton) {
    // In kiosk mode with exit button hidden - show nothing
    return null
  }

  return (
    <div className="kiosk-controls">
      {!isKioskMode ? (
        <button className="kiosk-control-btn kiosk-enter-btn" onClick={onEnterKioskMode}>
          <span className="icon">🖥️</span>
          Activer mode kiosque
        </button>
      ) : (
        <>
          <button
            className="kiosk-control-btn fullscreen-btn"
            onClick={onToggleFullscreen}
            title="Ctrl+Shift+F"
          >
            <span className="icon">{isFullscreen ? '⤓' : '⤢'}</span>
            {isFullscreen ? 'Quitter plein écran' : 'Plein écran'}
          </button>
          {showExitButton && (
            <button className="kiosk-control-btn exit-btn" onClick={onExitKioskMode}>
              <span className="icon">✕</span>
              Quitter mode kiosque
            </button>
          )}
        </>
      )}
    </div>
  )
}
