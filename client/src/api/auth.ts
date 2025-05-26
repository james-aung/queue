import apiClient from './client';

export interface User {
  id: number;
  email: string;
  username: string;
  phone_number?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  phone_number?: string;
}

class AuthService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('auth_token');
    if (this.token) {
      this.setAuthHeader();
    }
  }

  private setAuthHeader() {
    if (this.token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  }

  async login(username: string, password: string): Promise<User> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post<LoginResponse>('/auth/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    this.token = response.data.access_token;
    localStorage.setItem('auth_token', this.token);
    this.setAuthHeader();

    return response.data.user;
  }

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    // For now, we'll decode the JWT to get user info
    // This is a temporary solution until /auth/me endpoint is added
    if (!this.token) {
      throw new Error('Not authenticated');
    }
    
    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      return {
        id: payload.sub,
        email: payload.email || '',
        username: payload.username || payload.sub,
        phone_number: payload.phone_number,
        is_active: true,
        created_at: new Date().toISOString(),
      };
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  logout() {
    this.token = null;
    localStorage.removeItem('auth_token');
    this.setAuthHeader();
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }
}

export const authApi = new AuthService();