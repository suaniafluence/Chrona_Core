import { useEffect, useRef, useState } from 'react'

type VideoDevice = { id: string; label: string }

const CameraTest = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const [devices, setDevices] = useState<VideoDevice[]>([])
  const [selectedId, setSelectedId] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [active, setActive] = useState<boolean>(false)
  const currentStream = useRef<MediaStream | null>(null)

  const stopStream = () => {
    if (currentStream.current) {
      currentStream.current.getTracks().forEach((t) => t.stop())
      currentStream.current = null
      setActive(false)
    }
  }

  const startStream = async (deviceId?: string) => {
    setError('')
    try {
      const constraints: MediaStreamConstraints = {
        video: deviceId
          ? { deviceId: { exact: deviceId } }
          : { facingMode: { ideal: 'environment' } },
        audio: false,
      }
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      currentStream.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      setActive(true)
    } catch (e: any) {
      setError(e?.message || String(e))
      setActive(false)
    }
  }

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        // Prompt once to allow labels population on some browsers
        await navigator.mediaDevices.getUserMedia({ video: true })
      } catch (_) {
        // ignore – we will try again on start
      }
      try {
        const infos = await navigator.mediaDevices.enumerateDevices()
        const vids = infos
          .filter((d) => d.kind === 'videoinput')
          .map((d) => ({ id: d.deviceId, label: d.label || 'Camera' }))
        // Prefer back camera first if present
        vids.sort((a, b) => {
          const aback = /back|rear/i.test(a.label) ? -1 : 0
          const bback = /back|rear/i.test(b.label) ? -1 : 0
          return aback - bback
        })
        if (mounted) {
          setDevices(vids)
          if (vids[0]) setSelectedId(vids[0].id)
        }
      } catch (e: any) {
        if (mounted) setError(e?.message || String(e))
      }
    })()
    return () => {
      mounted = false
      stopStream()
    }
  }, [])

  return (
    <div style={{ maxWidth: 640, margin: '0 auto', textAlign: 'center' }}>
      <h2>Test Caméra</h2>
      <div style={{ margin: '12px 0' }}>
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          disabled={active}
          style={{ padding: '8px' }}
        >
          {devices.map((d) => (
            <option key={d.id} value={d.id}>
              {d.label}
            </option>
          ))}
        </select>
      </div>

      <div style={{ margin: '12px 0' }}>
        {!active ? (
          <button onClick={() => startStream(selectedId)} style={{ padding: '10px 16px' }}>
            Démarrer
          </button>
        ) : (
          <button onClick={stopStream} style={{ padding: '10px 16px' }}>
            Arrêter
          </button>
        )}
      </div>

      {error && (
        <div style={{ color: '#c0392b', marginBottom: 12 }}>Erreur: {error}</div>
      )}

      <video
        ref={videoRef}
        playsInline
        autoPlay
        muted
        style={{
          width: '100%',
          maxWidth: 640,
          maxHeight: 480,
          border: '1px solid black',
        }}
      />
      <p style={{ color: '#667eea' }}>Autorisez la caméra si demandé par le navigateur.</p>
    </div>
  )
}

export default CameraTest
