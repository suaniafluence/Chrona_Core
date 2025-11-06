import { useEffect, useRef } from 'react';
import { Download, X } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface QRCodeDisplayProps {
  token: string;
  expiresAt: string;
  deviceName: string;
  onClose: () => void;
}

export default function QRCodeDisplay({
  token,
  expiresAt,
  deviceName,
  onClose,
}: QRCodeDisplayProps) {
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
        // Generate new QR code
        new window.QRCode(containerRef.current, {
          text: token,
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
  }, [token]);

  const handleDownload = () => {
    const canvas = containerRef.current?.querySelector('canvas') as HTMLCanvasElement;
    if (canvas) {
      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/png');
      link.download = `qr-${deviceName}-${Date.now()}.png`;
      link.click();
    }
  };

  const handlePrint = () => {
    const canvas = containerRef.current?.querySelector('canvas') as HTMLCanvasElement;
    if (canvas) {
      const printWindow = window.open('', '', 'width=400,height=500');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>QR Code - ${deviceName}</title>
              <style>
                body { margin: 20px; text-align: center; font-family: Arial; }
                h2 { margin: 0 0 10px 0; }
                p { color: #666; margin: 5px 0; }
                img { max-width: 100%; }
              </style>
            </head>
            <body>
              <h2>${deviceName}</h2>
              <p>Expire le: ${format(new Date(expiresAt), 'dd MMM yyyy HH:mm:ss', { locale: fr })}</p>
              <img src="${canvas.toDataURL('image/png')}" />
              <p style="margin-top: 20px; font-size: 12px; color: #999;">
                Code d'accès temporaire - À usage unique
              </p>
            </body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    }
  };

  const expiresAtDate = new Date(expiresAt);
  const isExpired = expiresAtDate < new Date();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Code QR</h2>
            <p className="text-sm text-gray-600 mt-1">{deviceName}</p>
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

          {/* Expiration info */}
          <div className={`text-center mb-6 p-3 rounded-lg ${
            isExpired
              ? 'bg-red-50 text-red-700 border border-red-200'
              : 'bg-blue-50 text-blue-700 border border-blue-200'
          }`}>
            <p className="text-sm font-medium">
              {isExpired ? '🔴 Code expiré' : '🟢 Code valide'}
            </p>
            <p className="text-xs mt-1">
              Expire le {format(expiresAtDate, 'dd MMM yyyy HH:mm:ss', { locale: fr })}
            </p>
          </div>

          {/* Token display (for debugging) */}
          <div className="bg-gray-50 p-3 rounded-lg mb-6 border border-gray-200">
            <p className="text-xs text-gray-600 mb-2 font-medium">Token JWT:</p>
            <code className="text-xs text-gray-700 break-all font-mono">
              {token.substring(0, 50)}...
            </code>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={handleDownload}
              disabled={isExpired}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Télécharger</span>
            </button>
            <button
              onClick={handlePrint}
              disabled={isExpired}
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
