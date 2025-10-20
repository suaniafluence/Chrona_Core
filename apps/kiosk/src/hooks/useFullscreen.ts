/**
 * Custom hook to manage fullscreen mode for kiosk application
 */
import { useEffect, useState, useCallback } from 'react'

interface FullscreenHook {
  isFullscreen: boolean
  enterFullscreen: () => Promise<void>
  exitFullscreen: () => Promise<void>
  toggleFullscreen: () => Promise<void>
  isSupported: boolean
}

export const useFullscreen = (): FullscreenHook => {
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Check if Fullscreen API is supported
  const isSupported =
    document.fullscreenEnabled ||
    (document as any).webkitFullscreenEnabled ||
    (document as any).mozFullScreenEnabled ||
    (document as any).msFullscreenEnabled

  // Update fullscreen state when it changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      const fullscreenElement =
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).mozFullScreenElement ||
        (document as any).msFullscreenElement

      setIsFullscreen(!!fullscreenElement)
    }

    // Listen for fullscreen change events
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', handleFullscreenChange)

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
    }
  }, [])

  const enterFullscreen = useCallback(async () => {
    if (!isSupported) {
      console.warn('Fullscreen API is not supported')
      return
    }

    const element = document.documentElement

    try {
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if ((element as any).webkitRequestFullscreen) {
        await (element as any).webkitRequestFullscreen()
      } else if ((element as any).mozRequestFullScreen) {
        await (element as any).mozRequestFullScreen()
      } else if ((element as any).msRequestFullscreen) {
        await (element as any).msRequestFullscreen()
      }
    } catch (error) {
      console.error('Error entering fullscreen:', error)
    }
  }, [isSupported])

  const exitFullscreen = useCallback(async () => {
    if (!document.fullscreenElement && !(document as any).webkitFullscreenElement) {
      return
    }

    try {
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if ((document as any).webkitExitFullscreen) {
        await (document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        await (document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        await (document as any).msExitFullscreen()
      }
    } catch (error) {
      console.error('Error exiting fullscreen:', error)
    }
  }, [])

  const toggleFullscreen = useCallback(async () => {
    if (isFullscreen) {
      await exitFullscreen()
    } else {
      await enterFullscreen()
    }
  }, [isFullscreen, enterFullscreen, exitFullscreen])

  return {
    isFullscreen,
    enterFullscreen,
    exitFullscreen,
    toggleFullscreen,
    isSupported,
  }
}
