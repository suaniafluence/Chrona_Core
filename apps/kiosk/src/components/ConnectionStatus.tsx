import { useState, useEffect } from 'react'
import './ConnectionStatus.css'
import { healthCheck } from '../services/api'

export default function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const [lastCheck, setLastCheck] = useState<Date>(new Date())

  useEffect(() => {
    // Check connection every 10 seconds (or faster if offline)
    const checkConnection = async () => {
      try {
        await healthCheck()
        setIsOnline(true)
        setLastCheck(new Date())
      } catch (error) {
        setIsOnline(false)
        setLastCheck(new Date())
        console.error('Backend connection failed:', error)
      }
    }

    // Initial check
    checkConnection()

    // Listen to browser online/offline events (faster than health check)
    const handleOnline = () => {
      setIsOnline(true)
      setLastCheck(new Date())
    }
    const handleOffline = () => {
      setIsOnline(false)
      setLastCheck(new Date())
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Regular health checks every 10 seconds
    const interval = setInterval(checkConnection, 10000)

    return () => {
      clearInterval(interval)
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div
      data-testid="connection-status"
      className={`connection-status ${isOnline ? 'online' : 'offline'}`}
    >
      <div className="status-indicator" />
      <span className="status-text">
        {isOnline ? 'En ligne' : 'Hors ligne'}
      </span>
      <span className="status-time">
        {lastCheck.toLocaleTimeString('fr-FR', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>
    </div>
  )
}
