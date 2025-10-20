/**
 * Custom hook to manage kiosk mode with keyboard shortcuts
 *
 * Keyboard shortcuts:
 * - Ctrl+Shift+F: Toggle fullscreen
 * - Ctrl+Shift+K: Toggle kiosk mode (show/hide exit button)
 */
import { useEffect, useState, useCallback } from 'react'
import { useFullscreen } from './useFullscreen'

interface KioskModeHook {
  isKioskMode: boolean
  isFullscreen: boolean
  enterKioskMode: () => Promise<void>
  exitKioskMode: () => Promise<void>
  toggleFullscreen: () => Promise<void>
  showExitButton: boolean
  setShowExitButton: (show: boolean) => void
}

export const useKioskMode = (): KioskModeHook => {
  const { isFullscreen, enterFullscreen, exitFullscreen, toggleFullscreen, isSupported } =
    useFullscreen()
  const [isKioskMode, setIsKioskMode] = useState(false)
  const [showExitButton, setShowExitButton] = useState(true)

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+Shift+F: Toggle fullscreen
      if (event.ctrlKey && event.shiftKey && event.key === 'F') {
        event.preventDefault()
        toggleFullscreen()
      }

      // Ctrl+Shift+K: Toggle exit button visibility
      if (event.ctrlKey && event.shiftKey && event.key === 'K') {
        event.preventDefault()
        setShowExitButton((prev) => !prev)
      }

      // Prevent F11 (browser fullscreen) in kiosk mode
      if (isKioskMode && event.key === 'F11') {
        event.preventDefault()
      }

      // Prevent Esc key in kiosk mode (would exit fullscreen)
      if (isKioskMode && event.key === 'Escape') {
        event.preventDefault()
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [isKioskMode, toggleFullscreen])

  // Prevent context menu (right-click) in kiosk mode
  useEffect(() => {
    const handleContextMenu = (event: MouseEvent) => {
      if (isKioskMode) {
        event.preventDefault()
      }
    }

    window.addEventListener('contextmenu', handleContextMenu)

    return () => {
      window.removeEventListener('contextmenu', handleContextMenu)
    }
  }, [isKioskMode])

  // Prevent text selection in kiosk mode
  useEffect(() => {
    if (isKioskMode) {
      document.body.style.userSelect = 'none'
      document.body.style.webkitUserSelect = 'none'
    } else {
      document.body.style.userSelect = ''
      document.body.style.webkitUserSelect = ''
    }

    return () => {
      document.body.style.userSelect = ''
      document.body.style.webkitUserSelect = ''
    }
  }, [isKioskMode])

  const enterKioskMode = useCallback(async () => {
    setIsKioskMode(true)
    if (isSupported) {
      await enterFullscreen()
    }
  }, [isSupported, enterFullscreen])

  const exitKioskMode = useCallback(async () => {
    setIsKioskMode(false)
    if (isFullscreen) {
      await exitFullscreen()
    }
  }, [isFullscreen, exitFullscreen])

  // Auto-enter kiosk mode on mount (can be disabled via env var)
  useEffect(() => {
    const autoKiosk = import.meta.env.VITE_AUTO_KIOSK_MODE === 'true'
    if (autoKiosk) {
      enterKioskMode()
    }
  }, [enterKioskMode])

  return {
    isKioskMode,
    isFullscreen,
    enterKioskMode,
    exitKioskMode,
    toggleFullscreen,
    showExitButton,
    setShowExitButton,
  }
}
