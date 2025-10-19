import './ValidationResult.css'

interface ValidationResultProps {
  result: {
    success: boolean
    message: string
    punch_id?: number
    punched_at?: string
    user_id?: number
  } | null
}

const ValidationResult = ({ result }: ValidationResultProps) => {
  if (!result) return null

  const formatTime = (isoString?: string) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className={`validation-result ${result.success ? 'success' : 'error'}`}>
      <div className="result-icon">
        {result.success ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
      </div>

      <h2 className="result-title">
        {result.success ? 'Pointage validé !' : 'Erreur'}
      </h2>

      <p className="result-message">{result.message}</p>

      {result.success && result.punched_at && (
        <div className="result-details">
          <p className="result-time">{formatTime(result.punched_at)}</p>
          {result.user_id && (
            <p className="result-user">Utilisateur #{result.user_id}</p>
          )}
        </div>
      )}
    </div>
  )
}

export default ValidationResult
