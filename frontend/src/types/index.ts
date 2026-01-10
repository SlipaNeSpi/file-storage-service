export interface User {
  id: string;
  email: string;
  username?: string;
  role: 'user' | 'admin';
  created_at?: string;
  last_login?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface FileItem {
  id: string;
  filename: string;
  size: number;
  type: string;
  folder: string;
  created_at: string;
}

export interface FileMetadata extends FileItem {
  hash: string;
  updated_at: string;
}

export interface DashboardStats {
  users: {
    total: number;
    active: number;
    blocked: number;
    admins: number;
  };
  files: {
    total: number;
    deleted: number;
    active: number;
  };
  storage: {
    total_bytes: number;
    total_gb: number;
    average_file_size_mb: number;
  };
  file_types: Array<{
    type: string;
    count: number;
  }>;
}

export interface UserWithStats extends User {
  is_active: boolean;
  is_verified: boolean;
  stats: {
    file_count: number;
    total_size: number;
    total_size_mb: number;
  };
}
