import { useState } from 'react';
import { useAuthStore } from './store/authStore';
import { useFiles } from './hooks/useFiles';
import { Button } from './components/common/Button';
import { Input } from './components/common/Input';
import { Card } from './components/common/Card';
import { FileUpload } from './components/files/FileUpload';
import { FileList } from './components/files/FileList';
import toast, { Toaster } from 'react-hot-toast';

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const { login, user, isAuthenticated, logout } = useAuthStore();
  const { files, totalFiles, uploadFile, deleteFile, downloadFile, loadFiles } = useFiles();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast.success('Успешный вход!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка входа');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Вы вышли из системы');
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      await uploadFile(file);
    } finally {
      setIsUploading(false);
    }
  };

  // Экран после входа
  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <Toaster position="top-right" />

        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                📁 File Storage Service
              </h1>
              <p className="text-gray-600 mt-1">
                {user.email} • <span className="font-semibold">{user.role}</span>
              </p>
            </div>
            <Button variant="secondary" onClick={handleLogout}>
              Выйти
            </Button>
          </div>

          {/* Upload Section */}
          <Card className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Загрузить файл
            </h2>
            <FileUpload onUpload={handleUpload} isUploading={isUploading} />
          </Card>

          {/* Files List */}
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Мои файлы ({totalFiles})
              </h2>
              <Button variant="secondary" size="sm" onClick={() => loadFiles()}>
                🔄 Обновить
              </Button>
            </div>
            <FileList
              files={files}
              isLoading={false}
              onDownload={downloadFile}
              onDelete={deleteFile}
            />
          </Card>
        </div>
      </div>
    );
  }

  // Экран входа
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Toaster position="top-right" />
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Вход в систему
          </h1>
          <p className="text-gray-600">File Storage Service</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="example@mail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
          />

          <Input
            label="Пароль"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
          />

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            isLoading={isLoading}
          >
            Войти
          </Button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-2">Тестовые аккаунты:</p>
          <p className="text-xs text-gray-700">👤 user@example.com / User123!</p>
          <p className="text-xs text-gray-700">🔑 admin@example.com / Admin123</p>
        </div>
      </Card>
    </div>
  );
}

export default App;
