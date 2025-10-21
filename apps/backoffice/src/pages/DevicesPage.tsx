import { useEffect, useState } from 'react';
import { devicesAPI } from '@/lib/api';
import type { Device } from '@/types';
import { Smartphone, Ban, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterRevoked, setFilterRevoked] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    loadDevices();
  }, [filterRevoked]);

  const loadDevices = async () => {
    try {
      const data = await devicesAPI.getAll({ is_revoked: filterRevoked });
      setDevices(data);
      setError('');
    } catch (err) {
      setError('Erreur lors du chargement des appareils');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevokeDevice = async (deviceId: number) => {
    if (window.confirm('Voulez-vous vraiment révoquer cet appareil ?')) {
      try {
        await devicesAPI.revoke(deviceId);
        await loadDevices();
      } catch (err) {
        setError('Erreur lors de la révocation');
        console.error(err);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeDevices = devices.filter((d) => !d.is_revoked).length;
  const revokedDevices = devices.filter((d) => d.is_revoked).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Smartphone className="w-8 h-8 mr-3 text-primary-600" />
            Gestion des appareils
          </h1>
          <p className="text-gray-600 mt-1">
            {activeDevices} actifs • {revokedDevices} révoqués
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filtrer:</span>
          <button
            onClick={() => setFilterRevoked(undefined)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filterRevoked === undefined
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Tous ({devices.length})
          </button>
          <button
            onClick={() => setFilterRevoked(false)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filterRevoked === false
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Actifs ({activeDevices})
          </button>
          <button
            onClick={() => setFilterRevoked(true)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filterRevoked === true
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Révoqués ({revokedDevices})
          </button>
        </div>
      </div>

      {/* Devices table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilisateur
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statut
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Enregistré le
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Dernière activité
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {devices.map((device) => (
              <tr key={device.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  #{device.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {device.device_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  User #{device.user_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {device.is_revoked ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      <Ban className="w-3 h-3 mr-1" />
                      Révoqué
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Actif
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(new Date(device.registered_at), 'dd MMM yyyy', { locale: fr })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {device.last_seen_at
                    ? format(new Date(device.last_seen_at), 'dd MMM yyyy HH:mm', {
                        locale: fr,
                      })
                    : 'Jamais'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {!device.is_revoked && (
                    <button
                      onClick={() => handleRevokeDevice(device.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Révoquer
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {devices.length === 0 && (
          <div className="text-center py-12 text-gray-500">Aucun appareil trouvé</div>
        )}
      </div>
    </div>
  );
}
