import { useEffect, useState } from 'react';
import { kiosksAPI } from '@/lib/api';
import type { Kiosk, CreateKioskRequest } from '@/types';
import { Monitor, Plus, Power, MapPin, Key } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function KiosksPage() {
  const [kiosks, setKiosks] = useState<Kiosk[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createdKiosk, setCreatedKiosk] = useState<{
    kiosk_name: string;
    api_key: string;
  } | null>(null);

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
      // Generate API key immediately after creation to show once to the admin
      const keyResp = await kiosksAPI.generateApiKey(kiosk.id);
      setCreatedKiosk({ kiosk_name: kiosk.kiosk_name, api_key: keyResp.api_key });
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
        setError(detail || 'Conflit: nom ou empreinte déjà utilisés');
      } else {
        setError(detail || 'Erreur lors de la création du kiosque');
      }
      console.error('Create kiosk error:', err);
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeKiosks = kiosks.filter((k) => k.is_active).length;

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
            {activeKiosks} actifs sur {kiosks.length} kiosques
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

      {/* API Key Alert */}
      {createdKiosk && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <Key className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-900 mb-2">
                ClÃ© API gÃ©nÃ©rÃ©e - Copiez-la maintenant !
              </h3>
              <p className="text-sm text-yellow-700 mb-3">
                Cette clÃ© ne sera plus affichÃ©e. Configurez-la sur le kiosque :{' '}
                <strong>{createdKiosk.kiosk_name}</strong>
              </p>
              <div className="bg-white border border-yellow-300 rounded p-3 font-mono text-sm break-all">
                {createdKiosk.api_key}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(createdKiosk.api_key);
                  alert('ClÃ© API copiÃ©e !');
                }}
                className="mt-3 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
              >
                Copier la clÃ©
              </button>
              <button
                onClick={() => setCreatedKiosk(null)}
                className="mt-3 ml-2 px-4 py-2 bg-white border border-yellow-300 text-yellow-700 rounded-lg hover:bg-yellow-50 text-sm"
              >
                J'ai sauvegardÃ© la clÃ©
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Kiosks grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kiosks.map((kiosk) => (
          <div key={kiosk.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
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

            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                {kiosk.location}
              </div>
              <div className="text-xs text-gray-500">
                CrÃ©Ã© le {format(new Date(kiosk.created_at), 'dd MMM yyyy', { locale: fr })}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 break-all">
                ID: {kiosk.device_fingerprint.substring(0, 24)}...
              </p>
            </div>
          </div>
        ))}
      </div>

      {kiosks.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
          Aucun kiosque configurÃ©. CrÃ©ez-en un pour commencer.
        </div>
      )}

      {/* Create kiosk modal */}
      {showCreateModal && (
        <CreateKioskModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateKiosk}
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
  const [deviceFingerprint, setDeviceFingerprint] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ kiosk_name: kioskName, location, device_fingerprint: deviceFingerprint });
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">CrÃ©er un kiosque</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom du kiosque
            </label>
            <input
              type="text"
              value={kioskName}
              onChange={(e) => setKioskName(e.target.value)}
              required
              placeholder="EntrÃ©e-Ã‰tage1"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Localisation
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
              placeholder="Hall d'entrÃ©e, 1er Ã©tage"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Device Fingerprint
            </label>
            <input
              type="text"
              value={deviceFingerprint}
              onChange={(e) => setDeviceFingerprint(e.target.value)}
              required
              placeholder="UUID ou identifiant matÃ©riel"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
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
              CrÃ©er
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

