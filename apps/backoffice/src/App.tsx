import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './layouts/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import DevicesPage from './pages/DevicesPage';
import KiosksPage from './pages/KiosksPage';
import HRCodesPage from './pages/HRCodesPage';
import AuditLogsPage from './pages/AuditLogsPage';
import ReportsPage from './pages/ReportsPage';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="devices" element={<DevicesPage />} />
          <Route path="kiosks" element={<KiosksPage />} />
          <Route path="hr-codes" element={<HRCodesPage />} />
          <Route path="audit-logs" element={<AuditLogsPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
