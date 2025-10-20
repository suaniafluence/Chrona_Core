import { useState, useEffect } from 'react'
import './ConnectionStatus.css'
import { healthCheck } from '../services/api'

export default function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const [lastCheck, setLastCheck] = useState<Date>(new Date())

  useEffect(() => {
    // Check connection every 10 seconds
    const checkConnection = async () => {
      try {
        await healthCheck()
        setIsOnline(true)
        setLastCheck(new Date())
      } catch (error) {
        setIsOnline(false)
        console.error('Backend connection failed:', error)
      }
    }

    // Initial check
    checkConnection()

    // Regular checks
    const interval = setInterval(checkConnection, 10000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`connection-status ${isOnline ? 'online' : 'offline'}`}>
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
