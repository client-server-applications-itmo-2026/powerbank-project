import { apiClient } from './client';
import type {
  UserRetrieveResponse,
  RegisterUserRequest,
  UpdateAuthenticatedUserRequest,
} from '../types/api';

export const usersApi = {
  getMe: () => apiClient.get<UserRetrieveResponse>('/api/me'),
  updateMe: (data: UpdateAuthenticatedUserRequest) =>
    apiClient.patch<UserRetrieveResponse>('/api/me', data),
  register: (data: RegisterUserRequest) =>
    apiClient.post<UserRetrieveResponse>('/api/register', data, false),
};
