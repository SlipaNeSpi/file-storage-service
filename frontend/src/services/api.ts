import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Создаём axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истёк - выходим
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============= AUTH API =============
export const authAPI = {
  register: async (email: string, password: string) => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

// ============= FILES API =============
export const filesAPI = {
  upload: async (file: File, folder: string = 'root') => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/files/upload?folder=${folder}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (folder: string = 'root', skip: number = 0, limit: number = 20) => {
    const response = await api.get(`/files/?folder=${folder}&skip=${skip}&limit=${limit}`);
    return response.data;
  },

  download: async (fileId: string) => {
    const response = await api.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    return response;
  },

  delete: async (fileId: string) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },

  rename: async (fileId: string, newName: string) => {
    const response = await api.patch(`/files/${fileId}?new_name=${newName}`);
    return response.data;
  },

  getMetadata: async (fileId: string) => {
    const response = await api.get(`/files/${fileId}/metadata`);
    return response.data;
  },
};

// ============= ADMIN API =============
export const adminAPI = {
  getDashboard: async () => {
    const response = await api.get('/admin/dashboard');
    return response.data;
  },

  getUsers: async (skip: number = 0, limit: number = 100) => {
    const response = await api.get(`/admin/users?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getUserDetails: async (userId: string) => {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  toggleUserStatus: async (userId: string) => {
    const response = await api.patch(`/admin/users/${userId}/toggle-status`);
    return response.data;
  },

  changeUserRole: async (userId: string, newRole: 'user' | 'admin') => {
    const response = await api.patch(`/admin/users/${userId}/role?new_role=${newRole}`);
    return response.data;
  },

  deleteUser: async (userId: string) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  getAllFiles: async (skip: number = 0, limit: number = 100, fileType?: string) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (fileType) params.append('file_type', fileType);

    const response = await api.get(`/admin/files?${params}`);
    return response.data;
  },

  deleteFile: async (fileId: string) => {
    const response = await api.delete(`/admin/files/${fileId}`);
    return response.data;
  },

  getTopUsers: async (limit: number = 10) => {
    const response = await api.get(`/admin/top-users?limit=${limit}`);
    return response.data;
  },
};
