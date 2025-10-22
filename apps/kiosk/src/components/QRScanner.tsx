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
  const qrReaderRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [initDone, setInitDone] = useState(false)

  useEffect(() => {
    // Guard clause: wait for DOM element to be ready and not already initialized
    if (!qrReaderRef.current || initDone) {
      return
    }

    let isSubscribed = true

    const initScanner = async () => {
      try {
        console.log('QR > Starting scanner initialization...')

        // Double-check element exists
        if (!qrReaderRef.current) {
          console.error('QR > qr-reader ref lost during init')
          setError('Élément de scan introuvable')
          setIsLoading(false)
          return
        }

        // Check if component is still mounted
        if (!isSubscribed) {
          console.log('QR > Component unmounted, aborting init')
          return
        }

        console.log('QR > Creating Html5Qrcode instance...')
        const scanner = new Html5Qrcode('qr-reader')
        scannerRef.current = scanner

        const config = {
          fps: 10,
          qrbox: { width: 300, height: 300 },
          aspectRatio: 1.0,
        }

        // Try to get available cameras first, build candidates
        const candidates: Array<string | MediaTrackConstraints> = []
        try {
          console.log('QR > Enumerating cameras...')
          const devices = await Html5Qrcode.getCameras()
          console.log('QR > Available cameras:', devices)
          if (devices && devices.length > 0) {
            const back = devices.find(d => d.label?.toLowerCase().includes('back') || d.label?.toLowerCase().includes('rear'))
            if (back) candidates.push(back.id)
            // Add the rest (unique)
            devices.forEach(d => {
              if (!candidates.includes(d.id)) candidates.push(d.id)
            })
          }
        } catch (camErr) {
          console.warn('QR > Could not enumerate cameras, will try facingMode first:', camErr)
        }
        // Fallback by facingMode if no devices resolved
        if (candidates.length === 0) {
          candidates.push({ facingMode: 'environment' })
          candidates.push({ facingMode: 'user' })
        }

        console.log('QR > Starting camera with config:', config, 'candidates:', candidates)

        // Helper to attempt start with cascading candidates
        const tryStart = async (): Promise<void> => {
          let lastErr: any = null
          for (const c of candidates) {
            try {
              console.log('QR > Trying candidate:', c)
              await scanner.start(
                c as any,
                config,
                async (decodedText) => {
                  // Stop scanner temporarily during validation
                  await scanner.pause(true)

                  try {
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
                  console.debug('Scan error:', errorMessage)
                }
              )
              return
            } catch (e) {
              console.warn('QR > Candidate failed:', c, e)
              lastErr = e
              // Try next candidate
            }
          }
          throw lastErr || new Error('Aucune caméra disponible')
        }

        // Add a timeout to avoid hanging state without feedback
        const timeout = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('Timeout initialisation caméra (10s)')),
            10000)
        })

        await Promise.race([tryStart(), timeout])

        console.log('QR > Camera started successfully!')
        setIsLoading(false)
        setInitDone(true) // Mark initialization as complete
      } catch (err: any) {
        console.error('QR > Error initializing scanner:', err)
        const errorMsg = err.message || err.toString() || "Impossible d'initialiser la caméra"
        console.error('QR > Full error details:', err)
        setError(errorMsg)
        setIsLoading(false)
        setInitDone(true) // Prevent retry loop on error
      }
    }

    initScanner()

    return () => {
      console.log('QR > Cleanup: stopping scanner')
      isSubscribed = false
      if (scannerRef.current) {
        scannerRef.current
          .stop()
          .catch((err) => console.error('QR > Error stopping scanner:', err))
      }
    }
  }, [initDone, onScanSuccess, onScanError])

  if (error) {
    return (
      <div className="scanner-error">
        <h2>Erreur</h2>
        <p className="error-message">{error}</p>
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
      <div id="qr-reader" ref={qrReaderRef} className="qr-reader"></div>
      <p className="scanner-instruction">
        Positionnez le QR code dans le cadre
      </p>
    </div>
  )
}

export default QRScanner
