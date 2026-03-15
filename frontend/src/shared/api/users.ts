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
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.postFormData<UserRetrieveResponse>('/api/me/avatar', formData);
  },
  register: (data: RegisterUserRequest) =>
    apiClient.post<UserRetrieveResponse>('/api/register', data, false),
};
