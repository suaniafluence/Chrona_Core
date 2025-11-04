import { useEffect, useState } from 'react';
import { hrCodesAPI } from '@/lib/api';
import type { HRCode, CreateHRCodeRequest, HRCodeQRData } from '@/types';
import { KeyRound, Plus, CheckCircle, XCircle, Clock, QrCode } from 'lucide-react';
import { format, isPast, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import { QRCodeSVG } from 'qrcode.react';

export default function HRCodesPage() {
  const [hrCodes, setHRCodes] = useState<HRCode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrData, setQRData] = useState<HRCodeQRData | null>(null);
  const [includeUsed, setIncludeUsed] = useState(false);
  const [includeExpired, setIncludeExpired] = useState(false);

  useEffect(() => {
    loadHRCodes();
  }, [includeUsed, includeExpired]);

  const loadHRCodes = async () => {
    setIsLoading(true);
    try {
      const data = await hrCodesAPI.getAll({
        include_used: includeUsed,
        include_expired: includeExpired,
      });
      setHRCodes(data);
      setError('');
    } catch (err) {
      setError('Erreur lors du chargement des codes RH');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateHRCode = async (data: CreateHRCodeRequest) => {
    try {
      await hrCodesAPI.create(data);
      await loadHRCodes();
      setShowCreateModal(false);
      setError('');
    } catch (err) {
      setError('Erreur lors de la création du code RH');
      console.error(err);
    }
  };

  const handleGenerateQR = async (hrCodeId: number) => {
    try {
      const data = await hrCodesAPI.getQRData(hrCodeId);
      setQRData(data);
      setShowQRModal(true);
      setError('');
    } catch (err) {
      setError('Erreur lors de la génération du QR code');
      console.error(err);
    }
  };

  const getStatusBadge = (code: HRCode) => {
    if (code.is_used) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <CheckCircle className="w-3 h-3 mr-1" />
          Utilisé
        </span>
      );
    }
    if (code.expires_at && isPast(parseISO(code.expires_at))) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="w-3 h-3 mr-1" />
          Expiré
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <Clock className="w-3 h-3 mr-1" />
        Valide
      </span>
    );
  };

  const activeCodesCount = hrCodes.filter(
    (c) => !c.is_used && (!c.expires_at || !isPast(parseISO(c.expires_at)))
  ).length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <KeyRound className="w-8 h-8 mr-3 text-primary-600" />
            Codes RH (Onboarding)
          </h1>
          <p className="text-gray-600 mt-1">
            {activeCodesCount} codes valides sur {hrCodes.length} au total
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Nouveau code RH</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 flex gap-4">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={includeUsed}
            onChange={(e) => setIncludeUsed(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Afficher les codes utilisés</span>
        </label>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={includeExpired}
            onChange={(e) => setIncludeExpired(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Afficher les codes expirés</span>
        </label>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Code
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Employé
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Créé le
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Expire le
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {hrCodes.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    Aucun code RH trouvé
                  </td>
                </tr>
              ) : (
                hrCodes.map((code) => (
                  <tr key={code.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <code className="px-2 py-1 text-sm font-mono bg-gray-100 rounded">
                          {code.code}
                        </code>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {code.employee_name || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{code.employee_email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {format(parseISO(code.created_at), 'dd MMM yyyy HH:mm', {
                          locale: fr,
                        })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {code.expires_at
                          ? format(parseISO(code.expires_at), 'dd MMM yyyy HH:mm', {
                              locale: fr,
                            })
                          : 'Jamais'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(code)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button
                        onClick={() => handleGenerateQR(code.id)}
                        disabled={code.is_used}
                        className="inline-flex items-center px-3 py-1.5 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <QrCode className="w-4 h-4 mr-1" />
                        QR Code
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateHRCodeModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateHRCode}
        />
      )}

      {/* QR Code Modal */}
      {showQRModal && qrData && (
        <HRCodeQRModal
          qrData={qrData}
          onClose={() => {
            setShowQRModal(false);
            setQRData(null);
          }}
        />
      )}
    </div>
  );
}

function CreateHRCodeModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (data: CreateHRCodeRequest) => Promise<void>;
}) {
  const [employeeEmail, setEmployeeEmail] = useState('');
  const [employeeName, setEmployeeName] = useState('');
  const [expiresInDays, setExpiresInDays] = useState(7);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onCreate({
        employee_email: employeeEmail,
        employee_name: employeeName || undefined,
        expires_in_days: expiresInDays,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Créer un code RH
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Générer un code d'onboarding pour un nouvel employé
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email employé <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              value={employeeEmail}
              onChange={(e) => setEmployeeEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              placeholder="employee@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom complet (optionnel)
            </label>
            <input
              type="text"
              value={employeeName}
              onChange={(e) => setEmployeeName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              placeholder="Jean Dupont"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expiration (jours)
            </label>
            <input
              type="number"
              value={expiresInDays}
              onChange={(e) => setExpiresInDays(Number(e.target.value))}
              min={1}
              max={30}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Le code expirera dans {expiresInDays} jour{expiresInDays > 1 ? 's' : ''}
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Création...' : 'Créer le code'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function HRCodeQRModal({
  qrData,
  onClose,
}: {
  qrData: HRCodeQRData;
  onClose: () => void;
}) {
  const qrPayload = JSON.stringify({
    type: 'employee_onboarding',
    api_url: qrData.api_url,
    hr_code: qrData.hr_code,
    employee_email: qrData.employee_email,
    employee_name: qrData.employee_name,
  });

  const handleCopyConfig = () => {
    navigator.clipboard.writeText(qrPayload);
    alert('Configuration copiée dans le presse-papiers !');
  };

  const handleDownloadQR = () => {
    const svg = document.getElementById('hr-code-qr-code');
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
      downloadLink.download = `onboarding-${qrData.hr_code}-qr.png`;
      downloadLink.href = pngFile;
      downloadLink.click();
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">QR Code Onboarding Employé</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800 font-medium mb-2">
            📱 QR Code d'onboarding
          </p>
          <p className="text-sm text-blue-700">
            Scannez ce QR code avec l'application mobile Chrona pour démarrer le processus d'onboarding automatiquement.
          </p>
        </div>

        <div className="flex flex-col items-center space-y-4 mb-6">
          <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
            <QRCodeSVG
              id="hr-code-qr-code"
              value={qrPayload}
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
              <QrCode className="w-4 h-4" />
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
            <h3 className="font-semibold text-gray-900 mb-2">Informations de l'employé</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">Code RH:</dt>
                <dd className="font-medium text-gray-900">{qrData.hr_code}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Email:</dt>
                <dd className="font-medium text-gray-900">{qrData.employee_email}</dd>
              </div>
              {qrData.employee_name && (
                <div className="flex justify-between">
                  <dt className="text-gray-600">Nom:</dt>
                  <dd className="font-medium text-gray-900">{qrData.employee_name}</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-gray-600">URL API:</dt>
                <dd className="font-medium text-gray-900 break-all">{qrData.api_url}</dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
