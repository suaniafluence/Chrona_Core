import { useEffect, useRef } from 'react';
import { Download, X } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface HRCodeQRDisplayProps {
  hrCode: string;
  employeeEmail: string;
  employeeName: string | null;
  expiresAt: string | null;
  onClose: () => void;
}

export default function HRCodeQRDisplay({
  hrCode,
  employeeEmail,
  employeeName,
  expiresAt,
  onClose,
}: HRCodeQRDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Dynamically load qrcode library
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
    script.async = true;
    script.onload = () => {
      if (containerRef.current && window.QRCode) {
        // Clear previous QR code
        containerRef.current.innerHTML = '';
        // Generate new QR code from HR code string
        new window.QRCode(containerRef.current, {
          text: hrCode,
          width: 300,
          height: 300,
          colorDark: '#000000',
          colorLight: '#ffffff',
          correctLevel: window.QRCode.CorrectLevel.H,
        });
      }
    };
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [hrCode]);

  const handleDownload = () => {
    const canvas = containerRef.current?.querySelector('canvas') as HTMLCanvasElement;
    if (canvas) {
      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/png');
      link.download = `code-rh-${hrCode}-${Date.now()}.png`;
      link.click();
    }
  };

  const handlePrint = () => {
    const canvas = containerRef.current?.querySelector('canvas') as HTMLCanvasElement;
    if (canvas) {
      const printWindow = window.open('', '', 'width=500,height=600');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>Code RH - ${hrCode}</title>
              <style>
                body {
                  margin: 20px;
                  text-align: center;
                  font-family: Arial, sans-serif;
                  background: white;
                }
                .container {
                  max-width: 400px;
                  margin: 0 auto;
                  border: 2px solid #ddd;
                  padding: 30px;
                  border-radius: 8px;
                }
                h1 {
                  margin: 0 0 10px 0;
                  font-size: 28px;
                  color: #333;
                }
                .employee-info {
                  background: #f5f5f5;
                  padding: 15px;
                  border-radius: 6px;
                  margin-bottom: 20px;
                }
                .employee-info p {
                  margin: 5px 0;
                  font-size: 14px;
                }
                .email { color: #0066cc; font-weight: bold; }
                .qr-container {
                  margin: 20px 0;
                  padding: 20px;
                  background: white;
                  border: 2px solid #ddd;
                  border-radius: 6px;
                  display: inline-block;
                }
                img { max-width: 300px; }
                .instruction {
                  margin-top: 20px;
                  padding: 15px;
                  background: #e3f2fd;
                  border-left: 4px solid #2196F3;
                  text-align: left;
                  border-radius: 4px;
                  font-size: 12px;
                }
                .instruction h3 { margin-top: 0; }
                .instruction ol { margin: 10px 0; padding-left: 20px; }
                .instruction li { margin: 5px 0; }
                .footer {
                  margin-top: 20px;
                  font-size: 11px;
                  color: #999;
                  border-top: 1px solid #ddd;
                  padding-top: 15px;
                }
              </style>
            </head>
            <body>
              <div class="container">
                <h1>🔐 Code d'Onboarding</h1>

                <div class="employee-info">
                  <p><strong>${employeeName || 'Nouvel employé'}</strong></p>
                  <p class="email">${employeeEmail}</p>
                </div>

                <div class="qr-container">
                  <img src="${canvas.toDataURL('image/png')}" />
                </div>

                <div class="instruction">
                  <h3>📱 Comment utiliser ce code ?</h3>
                  <ol>
                    <li>Ouvrez l'application Chrona sur votre téléphone</li>
                    <li>Tapez sur "Nouvel employé"</li>
                    <li>Scannez ce code QR avec votre appareil</li>
                    <li>Le code d'onboarding sera rempli automatiquement</li>
                    <li>Complétez le processus d'inscription</li>
                  </ol>
                </div>

                ${
                  expiresAt
                    ? `<p style="color: #d32f2f; font-size: 12px; margin-top: 15px;">
                        ⚠️ Ce code expire le ${format(new Date(expiresAt), 'dd MMMM yyyy HH:mm', { locale: fr })}
                      </p>`
                    : ''
                }

                <div class="footer">
                  <p>Code RH: <strong>${hrCode}</strong></p>
                  <p>Généré le ${format(new Date(), 'dd MMMM yyyy HH:mm:ss', { locale: fr })}</p>
                  <p>⚠️ À usage unique - Conservez ce document en sécurité</p>
                </div>
              </div>
            </body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    }
  };

  const isExpired = expiresAt && new Date(expiresAt) < new Date();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Code RH QR</h2>
            <p className="text-sm text-gray-600 mt-1">{employeeName || employeeEmail}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-8">
          {/* QR Code Container */}
          <div className="flex justify-center mb-6">
            <div
              ref={containerRef}
              className={`bg-white border-2 border-gray-200 rounded-lg p-4 ${
                isExpired ? 'opacity-50' : ''
              }`}
            />
          </div>

          {/* Status info */}
          <div className={`text-center mb-6 p-3 rounded-lg ${
            isExpired
              ? 'bg-red-50 text-red-700 border border-red-200'
              : 'bg-green-50 text-green-700 border border-green-200'
          }`}>
            <p className="text-sm font-medium">
              {isExpired ? '🔴 Code expiré' : '🟢 Code valide'}
            </p>
            {expiresAt && (
              <p className="text-xs mt-1">
                Expire le {format(new Date(expiresAt), 'dd MMM yyyy HH:mm', { locale: fr })}
              </p>
            )}
          </div>

          {/* HR Code Display */}
          <div className="bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200 text-center">
            <p className="text-xs text-gray-600 mb-2 font-medium">CODE RH</p>
            <code className="text-lg font-bold text-gray-900 tracking-wider font-mono">
              {hrCode}
            </code>
          </div>

          {/* Employee info */}
          <div className="bg-blue-50 p-3 rounded-lg mb-6 border border-blue-200">
            <p className="text-xs text-blue-800">
              <strong>Employé:</strong> {employeeName || '-'}
            </p>
            <p className="text-xs text-blue-800 mt-1">
              <strong>Email:</strong> {employeeEmail}
            </p>
          </div>

          {/* Instructions */}
          <div className="bg-yellow-50 p-3 rounded-lg mb-6 border border-yellow-200">
            <p className="text-xs text-yellow-800 font-semibold mb-2">📱 Comment utiliser ?</p>
            <ol className="text-xs text-yellow-800 space-y-1 ml-4 list-decimal">
              <li>Ouvrir l'app Chrona</li>
              <li>Taper "Nouvel employé"</li>
              <li>Scanner ce QR code</li>
              <li>Code rempli automatiquement</li>
            </ol>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={handleDownload}
              disabled={isExpired || false}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Télécharger</span>
            </button>
            <button
              onClick={handlePrint}
              disabled={isExpired || false}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium"
            >
              Imprimer
            </button>
          </div>

          <button
            onClick={onClose}
            className="w-full mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}

// Extend Window interface to support QRCode library
declare global {
  interface Window {
    QRCode: any;
  }
}
