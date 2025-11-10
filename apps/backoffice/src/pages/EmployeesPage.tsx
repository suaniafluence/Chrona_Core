import { useEffect, useState } from 'react';
import { usersAPI, devicesAPI, hrCodesAPI } from '@/lib/api';
import type { User, Device, HRCode } from '@/types';
import {
  Users as UsersIcon,
  Plus,
  Trash2,
  Shield,
  Smartphone,
  Ban,
  CheckCircle,
  KeyRound,
  Clock,
  XCircle,
  ChevronDown,
  ChevronUp,
  QrCode,
} from 'lucide-react';
import { isPast, parseISO } from 'date-fns';
import DeviceManager from '@/components/DeviceManager';
import HRCodeQRDisplay from '@/components/HRCodeQRDisplay';

interface EmployeeRecord {
  email: string;
  name: string | null;
  // HR Code info
  hrCode: HRCode | null;
  // User account info
  user: User | null;
  // Devices info
  devices: Device[];
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<EmployeeRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [expandedEmails, setExpandedEmails] = useState<Set<string>>(new Set());
  const [selectedQRCode, setSelectedQRCode] = useState<HRCode | null>(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [usersData, devicesData, hrCodesData] = await Promise.all([
        usersAPI.getAll(),
        devicesAPI.getAll(),
        hrCodesAPI.getAll({ include_used: true, include_expired: true }),
      ]);

      // Build employee records by email
      const employeeMap = new Map<string, EmployeeRecord>();

      // Add from HR Codes
      hrCodesData.forEach((code) => {
        if (!employeeMap.has(code.employee_email)) {
          employeeMap.set(code.employee_email, {
            email: code.employee_email,
            name: code.employee_name,
            hrCode: code,
            user: null,
            devices: [],
          });
        } else {
          const emp = employeeMap.get(code.employee_email)!;
          emp.hrCode = code;
          if (!emp.name && code.employee_name) {
            emp.name = code.employee_name;
          }
        }
      });

      // Add/merge Users
      usersData.forEach((user) => {
        if (!employeeMap.has(user.email)) {
          employeeMap.set(user.email, {
            email: user.email,
            name: null,
            hrCode: null,
            user,
            devices: [],
          });
        } else {
          const emp = employeeMap.get(user.email)!;
          emp.user = user;
        }
      });

      // Add/merge Devices
      devicesData.forEach((device) => {
        const user = usersData.find((u) => u.id === device.user_id);
        if (user) {
          const emp = employeeMap.get(user.email);
          if (emp) {
            emp.devices.push(device);
          }
        }
      });

      setEmployees(Array.from(employeeMap.values()).sort((a, b) => a.email.localeCompare(b.email)));
      setError('');
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpanded = (email: string) => {
    const newExpanded = new Set(expandedEmails);
    if (newExpanded.has(email)) {
      newExpanded.delete(email);
    } else {
      newExpanded.add(email);
    }
    setExpandedEmails(newExpanded);
  };

  const handleDeleteUser = async (userId: number) => {
    if (window.confirm('Voulez-vous vraiment supprimer cet utilisateur ?')) {
      try {
        await usersAPI.delete(userId);
        await loadAllData();
      } catch (err) {
        setError('Erreur lors de la suppression');
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <UsersIcon className="w-8 h-8 mr-3 text-primary-600" />
            Gestion des employés
          </h1>
          <p className="text-gray-600 mt-1">{employees.length} employés</p>
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
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Employees Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12"></th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Employé
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Code RH
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Compte
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Appareils
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {employees.map((emp) => (
                <EmployeeRow
                  key={emp.email}
                  employee={emp}
                  isExpanded={expandedEmails.has(emp.email)}
                  onToggleExpand={() => toggleExpanded(emp.email)}
                  onDeleteUser={handleDeleteUser}
                  onDevicesChange={loadAllData}
                  onShowQRCode={setSelectedQRCode}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create HR Code Modal */}
      {showCreateModal && (
        <CreateHRCodeModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            loadAllData();
            setShowCreateModal(false);
          }}
        />
      )}

      {/* HR Code QR Display Modal */}
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

interface EmployeeRowProps {
  employee: EmployeeRecord;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onDeleteUser: (userId: number) => void;
  onDevicesChange: () => void;
  onShowQRCode: (hrCode: HRCode) => void;
}

function EmployeeRow({
  employee,
  isExpanded,
  onToggleExpand,
  onDeleteUser,
  onDevicesChange,
  onShowQRCode,
}: EmployeeRowProps) {
  const accountStatus = employee.user
    ? { status: 'created', user: employee.user }
    : { status: 'pending', user: null };
  const activeDevices = employee.devices.filter((d) => !d.is_revoked).length;
  const revokedDevices = employee.devices.filter((d) => d.is_revoked).length;

  return (
    <>
      <tr className="hover:bg-gray-50">
        <td className="px-4 py-4 text-center">
          {employee.devices.length > 0 && (
            <button onClick={onToggleExpand} className="text-gray-400 hover:text-gray-600">
              {isExpanded ? (
                <ChevronUp className="w-5 h-5" />
              ) : (
                <ChevronDown className="w-5 h-5" />
              )}
            </button>
          )}
        </td>

        {/* Employé */}
        <td className="px-6 py-4">
          <div className="text-sm font-medium text-gray-900">{employee.email}</div>
          {employee.name && <div className="text-xs text-gray-500">{employee.name}</div>}
        </td>

        {/* Code RH */}
        <td className="px-6 py-4">
          {employee.hrCode ? (
            <HRCodeBadge
              hrCode={employee.hrCode}
              onShowQRCode={() => onShowQRCode(employee.hrCode!)}
            />
          ) : (
            <span className="text-xs text-gray-400">Aucun code</span>
          )}
        </td>

        {/* Compte */}
        <td className="px-6 py-4">
          {accountStatus.status === 'created' && accountStatus.user ? (
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {accountStatus.user.role === 'admin' ? (
                  <>
                    <Shield className="w-3 h-3 mr-1" />
                    Admin
                  </>
                ) : (
                  'Employé'
                )}
              </span>
            </div>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              <Clock className="w-3 h-3 mr-1" />
              En attente
            </span>
          )}
        </td>

        {/* Appareils */}
        <td className="px-6 py-4">
          {employee.devices.length === 0 ? (
            <span className="text-xs text-gray-400">Aucun appareil</span>
          ) : (
            <div className="flex items-center space-x-1 text-sm">
              <Smartphone className="w-4 h-4 text-blue-600" />
              <span className="font-medium">{activeDevices}</span>
              {revokedDevices > 0 && (
                <>
                  <span className="text-gray-400">•</span>
                  <Ban className="w-4 h-4 text-red-600" />
                  <span className="text-red-600">{revokedDevices}</span>
                </>
              )}
            </div>
          )}
        </td>

        {/* Actions */}
        <td className="px-6 py-4 text-right space-x-2">
          {employee.user && (
            <button
              onClick={() => onDeleteUser(employee.user!.id)}
              className="inline-text-red-600 hover:text-red-900 text-sm"
              title="Supprimer l'utilisateur"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </td>
      </tr>

      {/* Expanded device manager row */}
      {isExpanded && employee.user && (
        <tr className="bg-gray-50">
          <td colSpan={6} className="px-6 py-4">
            <DeviceManager
              userEmail={employee.email}
              devices={employee.devices}
              onDevicesChange={onDevicesChange}
            />
          </td>
        </tr>
      )}
    </>
  );
}

function getHRCodeStatus(hrCode: HRCode | null) {
  if (!hrCode) return null;

  if (hrCode.is_used) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        <CheckCircle className="w-3 h-3 mr-1" />
        Utilisé
      </span>
    );
  }

  if (hrCode.expires_at && isPast(parseISO(hrCode.expires_at))) {
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
}

function HRCodeBadge({
  hrCode,
  onShowQRCode,
}: {
  hrCode: HRCode;
  onShowQRCode: () => void;
}) {
  const isValid = !hrCode.is_used && hrCode.expires_at && !isPast(parseISO(hrCode.expires_at));

  return (
    <div className="flex items-center space-x-2">
      <KeyRound className="w-4 h-4 text-blue-600" />
      <code className="px-2 py-1 text-xs font-mono bg-gray-100 rounded">{hrCode.code}</code>
      {getHRCodeStatus(hrCode)}
      {isValid && (
        <button
          onClick={onShowQRCode}
          className="ml-2 p-1 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded transition"
          title="Voir le code QR"
        >
          <QrCode className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

interface CreateHRCodeModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

function CreateHRCodeModal({ onClose, onSuccess }: CreateHRCodeModalProps) {
  const [employeeEmail, setEmployeeEmail] = useState('');
  const [employeeName, setEmployeeName] = useState('');
  const [expiresInDays, setExpiresInDays] = useState(7);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    try {
      await hrCodesAPI.create({
        employee_email: employeeEmail,
        employee_name: employeeName || undefined,
        expires_in_days: expiresInDays,
      });
      onSuccess();
    } catch (err) {
      setError('Erreur lors de la création du code RH');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Créer un code RH</h2>
          <p className="text-sm text-gray-600 mt-1">Générer un code d'onboarding pour un nouvel employé</p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

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
            <label className="block text-sm font-medium text-gray-700 mb-1">Nom complet (optionnel)</label>
            <input
              type="text"
              value={employeeName}
              onChange={(e) => setEmployeeName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              placeholder="Jean Dupont"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expiration (jours)</label>
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
