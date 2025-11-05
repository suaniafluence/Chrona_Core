import { useEffect, useState } from 'react';
import { hrCodesAPI } from '@/lib/api';
import type { HRCode, CreateHRCodeRequest } from '@/types';
import { KeyRound, Plus, CheckCircle, XCircle, Clock, QrCode } from 'lucide-react';
import { format, isPast, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import HRCodeQRDisplay from '@/components/HRCodeQRDisplay';

export default function HRCodesPage() {
  const [hrCodes, setHRCodes] = useState<HRCode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [includeUsed, setIncludeUsed] = useState(false);
  const [includeExpired, setIncludeExpired] = useState(false);
  const [selectedQRCode, setSelectedQRCode] = useState<HRCode | null>(null);

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
                      {!code.is_used && code.expires_at && !isPast(parseISO(code.expires_at)) && (
                        <button
                          onClick={() => setSelectedQRCode(code)}
                          className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded transition"
                          title="Générer QR code pour cet employé"
                        >
                          <QrCode className="w-4 h-4" />
                          <span className="hidden sm:inline">QR</span>
                        </button>
                      )}
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

      {/* QR Code Display Modal */}
      {selectedQRCode && (
        <HRCodeQRDisplay
          hrCode={selectedQRCode.code}
          employeeEmail={selectedQRCode.employee_email}
          employeeName={selectedQRCode.employee_name}
          expiresAt={selectedQRCode.expires_at}
          onClose={() => setSelectedQRCode(null)}
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
