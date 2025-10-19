import { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import { validatePunch } from '../services/api'
import './QRScanner.css'

interface QRScannerProps {
  onScanSuccess: (result: any) => void
  onScanError: (error: string) => void
}

const QRScanner = ({ onScanSuccess, onScanError }: QRScannerProps) => {
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initScanner = async () => {
      try {
        const scanner = new Html5Qrcode('qr-reader')
        scannerRef.current = scanner

        const config = {
          fps: 10,
          qrbox: { width: 300, height: 300 },
          aspectRatio: 1.0,
        }

        await scanner.start(
          { facingMode: 'environment' },
          config,
          async (decodedText) => {
            // Stop scanner temporarily during validation
            await scanner.pause(true)

            try {
              // The QR code contains the JWT token
              const result = await validatePunch(decodedText)
              onScanSuccess(result)
            } catch (err: any) {
              const errorMsg = err.response?.data?.detail || err.message || 'Erreur de validation'
              onScanError(errorMsg)
            }

            // Resume scanner after a delay
            setTimeout(async () => {
              try {
                await scanner.resume()
              } catch (resumeErr) {
                console.error('Error resuming scanner:', resumeErr)
              }
            }, 3000)
          },
          (errorMessage) => {
            // Ignore scanning errors (camera still searching for QR)
            console.debug('Scan error:', errorMessage)
          }
        )

        setIsLoading(false)
      } catch (err: any) {
        console.error('Error initializing scanner:', err)
        setError(err.message || 'Impossible d\'initialiser la caméra')
        setIsLoading(false)
      }
    }

    initScanner()

    return () => {
      if (scannerRef.current) {
        scannerRef.current
          .stop()
          .catch((err) => console.error('Error stopping scanner:', err))
      }
    }
  }, [onScanSuccess, onScanError])

  if (error) {
    return (
      <div className="scanner-error">
        <h2>Erreur</h2>
        <p>{error}</p>
        <p className="scanner-help">
          Assurez-vous que la caméra est autorisée et fonctionnelle.
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="scanner-loading">
        <div className="spinner"></div>
        <p>Initialisation de la caméra...</p>
      </div>
    )
  }

  return (
    <div className="scanner-container">
      <div id="qr-reader" className="qr-reader"></div>
      <p className="scanner-instruction">
        Positionnez le QR code dans le cadre
      </p>
    </div>
  )
}

export default QRScanner
