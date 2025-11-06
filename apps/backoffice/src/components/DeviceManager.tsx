import { useState } from 'react';
import { devicesAPI } from '@/lib/api';
import type { Device, CreateDeviceRequest, QRCodeToken } from '@/types';
import { Plus, Smartphone, Ban, CheckCircle, QrCode, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import QRCodeDisplay from './QRCodeDisplay';

interface DeviceManagerProps {
  userEmail: string;
  devices: Device[];
  onDevicesChange: () => void;
}

export default function DeviceManager({
  userEmail,
  devices,
  onDevicesChange,
}: DeviceManagerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [qrToken, setQrToken] = useState<QRCodeToken | null>(null);
  const [qrDeviceName, setQrDeviceName] = useState<string>('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateDevice = async (data: CreateDeviceRequest) => {
    setIsLoading(true);
    setError('');
    try {
      await devicesAPI.create(data);
      setIsCreating(false);
      onDevicesChange();
    } catch (err) {
      setError('Erreur lors de la création de l\'appareil');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateQR = async (device: Device) => {
    setIsLoading(true);
    setError('');
    try {
      const token = await devicesAPI.generateQRToken(device.id);
      setQrToken(token);
      setQrDeviceName(device.device_name);
    } catch (err) {
      setError('Erreur lors de la génération du code QR');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevokeDevice = async (deviceId: number) => {
    if (window.confirm('Révoquer cet appareil ? Il ne pourra plus être utilisé.')) {
      setError('');
      try {
        await devicesAPI.revoke(deviceId);
        onDevicesChange();
      } catch (err) {
        setError('Erreur lors de la révocation');
        console.error(err);
      }
    }
  };

  const activeDevices = devices.filter((d) => !d.is_revoked);
  const revokedDevices = devices.filter((d) => d.is_revoked);

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Header avec bouton */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          📱 Appareils ({devices.length})
        </h3>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center space-x-1 px-3 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Ajouter un appareil</span>
        </button>
      </div>

      {/* Liste des appareils */}
      {devices.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
          <Smartphone className="w-12 h-12 text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">Aucun appareil enregistré</p>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Appareils actifs */}
          {activeDevices.map((device) => (
            <div
              key={device.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <h4 className="font-medium text-gray-900">{device.device_name}</h4>
                  </div>
                  <div className="text-xs text-gray-500 space-y-1 ml-6">
                    <p>
                      <span className="text-gray-600">Fingerprint:</span> {device.device_fingerprint}
                    </p>
                    <p>
                      Enregistré le:{' '}
                      {format(new Date(device.registered_at), 'dd MMM yyyy HH:mm', { locale: fr })}
                    </p>
                    {device.last_seen_at && (
                      <p>
                        Dernière activité:{' '}
                        {format(new Date(device.last_seen_at), 'dd MMM yyyy HH:mm', { locale: fr })}
                      </p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleGenerateQR(device)}
                    disabled={isLoading}
                    className="flex items-center space-x-1 px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    title="Générer un code QR pour cet appareil"
                  >
                    <QrCode className="w-4 h-4" />
                    <span className="hidden sm:inline">QR</span>
                  </button>
                  <button
                    onClick={() => handleRevokeDevice(device.id)}
                    className="flex items-center space-x-1 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
                    title="Révoquer cet appareil"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Appareils révoqués */}
          {revokedDevices.length > 0 && (
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Appareils révoqués ({revokedDevices.length})
              </h4>
              <div className="space-y-2">
                {revokedDevices.map((device) => (
                  <div
                    key={device.id}
                    className="bg-red-50 border border-red-200 rounded-lg p-3 opacity-75"
                  >
                    <div className="flex items-center space-x-2">
                      <Ban className="w-4 h-4 text-red-600" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-900">{device.device_name}</p>
                        <p className="text-xs text-red-700">Révoqué</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal de création */}
      {isCreating && (
        <AddDeviceModal
          userEmail={userEmail}
          onClose={() => setIsCreating(false)}
          onSubmit={handleCreateDevice}
          isLoading={isLoading}
        />
      )}

      {/* Affichage du QR code */}
      {qrToken && (
        <QRCodeDisplay
          token={qrToken.qr_token}
          expiresAt={qrToken.expires_at}
          deviceName={qrDeviceName}
          onClose={() => setQrToken(null)}
        />
      )}
    </div>
  );
}

interface AddDeviceModalProps {
  userEmail: string;
  onClose: () => void;
  onSubmit: (data: CreateDeviceRequest) => Promise<void>;
  isLoading: boolean;
}

function AddDeviceModal({
  userEmail,
  onClose,
  onSubmit,
  isLoading,
}: AddDeviceModalProps) {
  const [deviceName, setDeviceName] = useState('');
  const [deviceFingerprint, setDeviceFingerprint] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!deviceName.trim()) {
      setError('Le nom de l\'appareil est requis');
      return;
    }

    if (!deviceFingerprint.trim()) {
      setError('Le fingerprint de l\'appareil est requis');
      return;
    }

    try {
      await onSubmit({
        device_name: deviceName,
        device_fingerprint: deviceFingerprint,
      });
    } catch (err) {
      setError('Erreur lors de la création de l\'appareil');
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Ajouter un appareil</h2>
          <p className="text-sm text-gray-600 mt-1">Pour: {userEmail}</p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom de l'appareil <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
              placeholder="ex: iPhone 14 Pro, Samsung Galaxy S23"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Donnez un nom facilement reconnaissable pour cet appareil
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fingerprint de l'appareil <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={deviceFingerprint}
              onChange={(e) => setDeviceFingerprint(e.target.value)}
              placeholder="ex: device_fp_alice_001"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Identifiant unique de l'appareil fourni par l'app mobile
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              💡 Le fingerprint est généré automatiquement par l'application mobile lors de
              l'enregistrement du device.
            </p>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              disabled={isLoading}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Création...' : 'Créer l\'appareil'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
