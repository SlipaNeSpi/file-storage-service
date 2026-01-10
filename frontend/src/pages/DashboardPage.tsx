import React from 'react';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Добро пожаловать, {user?.email}!
            </h1>
            <p className="text-gray-600 mt-1">
              Роль: <span className="font-semibold">{user?.role}</span>
            </p>
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            Выйти
          </Button>
        </div>

        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Мои файлы
          </h2>
          <p className="text-gray-600">
            Здесь будет список ваших файлов (следующий шаг)
          </p>
        </Card>
      </div>
    </div>
  );
};
