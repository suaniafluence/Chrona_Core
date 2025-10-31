import { useEffect, useState } from 'react';
import { kiosksAPI } from '@/lib/api';
import type { Kiosk, CreateKioskRequest, KioskConfigData } from '@/types';
import { Monitor, Plus, Power, MapPin, QrCode, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { format, differenceInMinutes } from 'date-fns';
import { fr } from 'date-fns/locale';
import { QRCodeSVG } from 'qrcode.react';

export default function KiosksPage() {
  const [kiosks, setKiosks] = useState<Kiosk[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrConfigData, setQRConfigData] = useState<KioskConfigData | null>(null);

  useEffect(() => {
    loadKiosks();
  }, []);

  const loadKiosks = async () => {
    try {
      const data = await kiosksAPI.getAll();
      setKiosks(data);
      setError('');
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message;
      if (status === 401 || status === 403) {
        setError('Session expirée. Veuillez vous reconnecter.');
        window.location.href = '/login';
      } else {
        setError(detail || 'Erreur lors du chargement des kiosques');
      }
      console.error('Load kiosks error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateKiosk = async (data: CreateKioskRequest) => {
    try {
      const kiosk = await kiosksAPI.create(data);
      // Generate API key immediately after creation to show QR code
      const configData = await kiosksAPI.generateApiKey(kiosk.id);
      setQRConfigData(configData);
      setShowQRModal(true);
      await loadKiosks();
      setShowCreateModal(false);
      setError('');
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message;
      if (status === 401 || status === 403) {
        setError('Session expirée. Veuillez vous reconnecter.');
        window.location.href = '/login';
      } else if (status === 409) {
        setError(detail || 'Conflit: nom déjà utilisé');
      } else {
        setError(detail || 'Erreur lors de la création du kiosque');
      }
      console.error('Create kiosk error:', err);
    }
  };

  const handleRegenerateApiKey = async (kioskId: number) => {
    try {
      const configData = await kiosksAPI.generateApiKey(kioskId);
      setQRConfigData(configData);
      setShowQRModal(true);
      setError('');
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message;
      if (status === 401 || status === 403) {
        setError('Session expirée. Veuillez vous reconnecter.');
        window.location.href = '/login';
      } else {
        setError(detail || 'Erreur lors de la génération de la clé API');
      }
      console.error('Generate API key error:', err);
    }
  };

  const handleToggleActive = async (kioskId: number, currentStatus: boolean) => {
    try {
      await kiosksAPI.update(kioskId, { is_active: !currentStatus });
      await loadKiosks();
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message;
      if (status === 401 || status === 403) {
        setError('Session expirée. Veuillez vous reconnecter.');
        window.location.href = '/login';
      } else {
        setError(detail || 'Erreur lors de la modification du statut');
      }
      console.error('Toggle kiosk status error:', err);
    }
  };

  const getKioskStatus = (kiosk: Kiosk): 'online' | 'offline' | 'unknown' => {
    if (!kiosk.last_heartbeat_at) return 'unknown';

    const lastHeartbeat = new Date(kiosk.last_heartbeat_at);
    const minutesSinceLastHeartbeat = differenceInMinutes(new Date(), lastHeartbeat);

    // Consider online if heartbeat within last 5 minutes
    return minutesSinceLastHeartbeat <= 5 ? 'online' : 'offline';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeKiosks = kiosks.filter((k) => k.is_active).length;
  const onlineKiosks = kiosks.filter((k) => getKioskStatus(k) === 'online').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Monitor className="w-8 h-8 mr-3 text-primary-600" />
            Gestion des kiosques
          </h1>
          <p className="text-gray-600 mt-1">
            {onlineKiosks} en ligne · {activeKiosks} actifs sur {kiosks.length} kiosques
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Nouveau kiosque</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Kiosks grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kiosks.map((kiosk) => {
          const status = getKioskStatus(kiosk);
          return (
            <div key={kiosk.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div
                    className={`p-3 rounded-lg ${
                      kiosk.is_active ? 'bg-green-100' : 'bg-gray-100'
                    }`}
                  >
                    <Monitor
                      className={`w-6 h-6 ${
                        kiosk.is_active ? 'text-green-600' : 'text-gray-400'
                      }`}
                    />
                  </div>
                  {status === 'online' && (
                    <div title="En ligne">
                      <Wifi className="w-5 h-5 text-green-500" />
                    </div>
                  )}
                  {status === 'offline' && (
                    <div title="Hors ligne">
                      <WifiOff className="w-5 h-5 text-red-500" />
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleToggleActive(kiosk.id, kiosk.is_active)}
                  className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                    kiosk.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <Power className="w-3 h-3 mr-1" />
                  {kiosk.is_active ? 'Actif' : 'Inactif'}
                </button>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">{kiosk.kiosk_name}</h3>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-2" />
                  {kiosk.location}
                </div>
                <div className="text-xs text-gray-500">
                  Créé le {format(new Date(kiosk.created_at), 'dd MMM yyyy', { locale: fr })}
                </div>
                {kiosk.last_heartbeat_at && (
                  <div className="text-xs text-gray-500">
                    Dernier signal: {format(new Date(kiosk.last_heartbeat_at), 'dd/MM/yyyy HH:mm', { locale: fr })}
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 flex space-x-2">
                <button
                  onClick={() => handleRegenerateApiKey(kiosk.id)}
                  className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition text-sm"
                >
                  <QrCode className="w-4 h-4" />
                  <span>Voir QR Code</span>
                </button>
              </div>

              <div className="mt-2 text-xs text-gray-400 break-all">
                ID: {kiosk.device_fingerprint.substring(0, 24)}...
              </div>
            </div>
          );
        })}
      </div>

      {kiosks.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
          Aucun kiosque configuré. Créez-en un pour commencer.
        </div>
      )}

      {/* Create kiosk modal */}
      {showCreateModal && (
        <CreateKioskModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateKiosk}
        />
      )}

      {/* QR Code modal */}
      {showQRModal && qrConfigData && (
        <QRCodeModal
          configData={qrConfigData}
          onClose={() => {
            setShowQRModal(false);
            setQRConfigData(null);
          }}
        />
      )}
    </div>
  );
}

function CreateKioskModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (data: CreateKioskRequest) => void;
}) {
  const [kioskName, setKioskName] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ kiosk_name: kioskName, location });
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Créer un kiosque</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom du kiosque *
            </label>
            <input
              type="text"
              value={kioskName}
              onChange={(e) => setKioskName(e.target.value)}
              required
              placeholder="Entrée-Étage1"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Localisation *
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
              placeholder="Hall d'entrée, 1er étage"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-700">
              Un identifiant unique sera généré automatiquement pour ce kiosque.
            </p>
          </div>
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Créer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function QRCodeModal({
  configData,
  onClose,
}: {
  configData: KioskConfigData;
  onClose: () => void;
}) {
  const qrData = JSON.stringify({
    apiBaseUrl: configData.api_url,
    kioskId: configData.kiosk_id,
    kioskApiKey: configData.api_key,
    kioskName: configData.kiosk_name,
    location: configData.location,
    punchType: 'clock_in',
  });

  const handleCopyConfig = () => {
    navigator.clipboard.writeText(qrData);
    alert('Configuration copiée dans le presse-papiers !');
  };

  const handleDownloadQR = () => {
    const svg = document.getElementById('kiosk-qr-code');
    if (!svg) return;

    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx?.drawImage(img, 0, 0);
      const pngFile = canvas.toDataURL('image/png');

      const downloadLink = document.createElement('a');
      downloadLink.download = `kiosk-${configData.kiosk_name}-qr.png`;
      downloadLink.href = pngFile;
      downloadLink.click();
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Configuration du kiosque</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800 font-medium mb-2">
            ⚠️ Cette clé API ne sera plus affichée !
          </p>
          <p className="text-sm text-yellow-700">
            Scannez ce QR code avec l'application kiosque pour le configurer automatiquement.
            Si vous perdez cette clé, vous devrez en générer une nouvelle.
          </p>
        </div>

        <div className="flex flex-col items-center space-y-4 mb-6">
          <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
            <QRCodeSVG
              id="kiosk-qr-code"
              value={qrData}
              size={300}
              level="H"
              includeMargin={true}
            />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleDownloadQR}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Télécharger QR Code</span>
            </button>
            <button
              onClick={handleCopyConfig}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
            >
              <span>Copier la configuration</span>
            </button>
          </div>
        </div>

        <div className="space-y-3 text-sm">
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Informations du kiosque</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">Nom:</dt>
                <dd className="font-medium text-gray-900">{configData.kiosk_name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">ID:</dt>
                <dd className="font-medium text-gray-900">{configData.kiosk_id}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Localisation:</dt>
                <dd className="font-medium text-gray-900">{configData.location}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">URL API:</dt>
                <dd className="font-medium text-gray-900 break-all">{configData.api_url}</dd>
              </div>
            </dl>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Clé API (à ne pas partager)</h3>
            <div className="bg-white border border-gray-300 rounded p-3 font-mono text-xs break-all">
              {configData.api_key}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            J'ai sauvegardé la configuration
          </button>
        </div>
      </div>
    </div>
  );
}
