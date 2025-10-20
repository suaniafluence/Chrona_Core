import { useState } from 'react';
import { reportsAPI } from '@/lib/api';
import { FileText, Download, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function ReportsPage() {
  const [fromDate, setFromDate] = useState(
    format(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd')
  );
  const [toDate, setToDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [userId, setUserId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDownloadReport = async (formatType: 'json' | 'csv' | 'pdf') => {
    setIsLoading(true);
    setError('');

    try {
      const params: {
        from: string;
        to: string;
        user_id?: number;
        format?: 'json' | 'csv' | 'pdf';
      } = {
        from: fromDate,
        to: toDate,
        format: formatType,
      };

      if (userId) {
        params.user_id = parseInt(userId);
      }

      const data = await reportsAPI.getAttendance(params);

      // Handle download based on format
      if (formatType === 'json') {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        downloadBlob(blob, `rapport-presence-${fromDate}-${toDate}.json`);
      } else {
        // For CSV and PDF, data is already a Blob
        downloadBlob(
          data as Blob,
          `rapport-presence-${fromDate}-${toDate}.${formatType}`
        );
      }
    } catch (err) {
      setError('Erreur lors de la génération du rapport');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <FileText className="w-8 h-8 mr-3 text-primary-600" />
          Rapports de présence
        </h1>
        <p className="text-gray-600 mt-1">
          Générez des rapports de présence pour analyse ou conformité RGPD
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Report configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration du rapport</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Date de début
            </label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Date de fin
            </label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filtrer par utilisateur (optionnel)
            </label>
            <input
              type="number"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="ID utilisateur (laisser vide pour tous)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Download options */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Format d'export</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => handleDownloadReport('json')}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition disabled:opacity-50"
          >
            <Download className="w-8 h-8 text-primary-600 mb-3" />
            <h3 className="font-medium text-gray-900">JSON</h3>
            <p className="text-sm text-gray-600 mt-1 text-center">
              Format structuré pour analyse
            </p>
          </button>

          <button
            onClick={() => handleDownloadReport('csv')}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition disabled:opacity-50"
          >
            <Download className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="font-medium text-gray-900">CSV</h3>
            <p className="text-sm text-gray-600 mt-1 text-center">
              Compatible Excel/Sheets
            </p>
          </button>

          <button
            onClick={() => handleDownloadReport('pdf')}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition disabled:opacity-50"
          >
            <Download className="w-8 h-8 text-red-600 mb-3" />
            <h3 className="font-medium text-gray-900">PDF</h3>
            <p className="text-sm text-gray-600 mt-1 text-center">
              Rapport imprimable
            </p>
          </button>
        </div>

        {isLoading && (
          <div className="mt-6 flex items-center justify-center text-primary-600">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div>
            <span>Génération du rapport en cours...</span>
          </div>
        )}
      </div>

      {/* GDPR info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Information RGPD</h3>
        <p className="text-sm text-blue-700">
          Les rapports générés contiennent des données personnelles. Assurez-vous de respecter
          les obligations RGPD lors de leur utilisation et stockage. Conservation recommandée :
          5 ans maximum selon la législation du travail française.
        </p>
      </div>
    </div>
  );
}
