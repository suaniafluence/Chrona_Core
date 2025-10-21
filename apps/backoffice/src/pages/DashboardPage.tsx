import { useEffect, useState } from 'react';
import { dashboardAPI } from '@/lib/api';
import type { DashboardStats, Punch } from '@/types';
import { Users, Smartphone, Monitor, Clock, TrendingUp, Activity } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentPunches, setRecentPunches] = useState<Punch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch real dashboard stats from backend
      const data = await dashboardAPI.getStats();
      setStats(data);
      setRecentPunches(data.recent_punches || []);
      setError('');
    } catch (err) {
      setError('Erreur lors du chargement des statistiques');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  const statCards = [
    {
      name: 'Utilisateurs',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'bg-blue-500',
      trend: '+2 ce mois',
    },
    {
      name: 'Appareils',
      value: stats?.total_devices || 0,
      icon: Smartphone,
      color: 'bg-green-500',
      trend: '+3 ce mois',
    },
    {
      name: 'Kiosques actifs',
      value: `${stats?.active_kiosks || 0}/${stats?.total_kiosks || 0}`,
      icon: Monitor,
      color: 'bg-purple-500',
      trend: 'Tous en ligne',
    },
    {
      name: "Pointages aujourd'hui",
      value: stats?.today_punches || 0,
      icon: Clock,
      color: 'bg-orange-500',
      trend: `${stats?.today_users || 0} employés`,
    },
  ];

  // Generate mock weekly data for charts
  const weeklyData = [
    { day: 'Lun', punches: 45 },
    { day: 'Mar', punches: 52 },
    { day: 'Mer', punches: 48 },
    { day: 'Jeu', punches: 50 },
    { day: 'Ven', punches: 46 },
    { day: 'Sam', punches: 12 },
    { day: 'Dim', punches: 8 },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Tableau de bord</h1>
        <p className="opacity-90">
          Bienvenue sur le back-office Chrona. Voici un aperçu de l'activité.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card) => (
          <div key={card.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`${card.color} p-3 rounded-lg`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">{card.name}</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{card.value}</p>
            <p className="text-sm text-gray-500">{card.trend}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly punches chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-600" />
            Pointages cette semaine
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="punches" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Activity trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
            Tendance d'activité
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="punches"
                stroke="#0ea5e9"
                strokeWidth={2}
                dot={{ fill: '#0ea5e9' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-primary-600" />
            Activité récente
          </h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentPunches.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              Aucune activité récente
            </div>
          ) : (
            recentPunches.slice(0, 10).map((punch) => (
              <div key={punch.id} className="px-6 py-4 hover:bg-gray-50 transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        punch.punch_type === 'clock_in' ? 'bg-green-500' : 'bg-orange-500'
                      }`}
                    ></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Utilisateur #{punch.user_id}
                      </p>
                      <p className="text-xs text-gray-500">
                        {punch.punch_type === 'clock_in' ? 'Arrivée' : 'Départ'} • Kiosque #
                        {punch.kiosk_id}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-900">
                      {format(new Date(punch.punched_at), 'HH:mm:ss')}
                    </p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(punch.punched_at), 'dd MMM yyyy', { locale: fr })}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
