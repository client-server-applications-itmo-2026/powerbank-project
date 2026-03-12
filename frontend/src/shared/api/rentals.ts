import { apiClient } from './client';
import type {
  RentalSchema,
  PagedRentalSchema,
  StartRentalRequest,
  CompleteRentalRequest,
  TariffSchema,
} from '../types/api';

export const rentalsApi = {
  getRentalById: (rental_id: number) =>
    apiClient.post<RentalSchema>(`/api/retnals?rental_id=${rental_id}`, {}),

  getMyRentals: (params?: { limit?: number; offset?: number }) => {
    const qs = new URLSearchParams();
    if (params?.limit != null) qs.set('limit', String(params.limit));
    if (params?.offset != null) qs.set('offset', String(params.offset));
    const query = qs.toString();
    return apiClient.get<PagedRentalSchema>(`/api/me/rentals${query ? '?' + query : ''}`);
  },

  startRental: (data: StartRentalRequest) =>
    apiClient.post<RentalSchema>('/api/start-rental', data),

  completeRental: (data: CompleteRentalRequest) =>
    apiClient.post<RentalSchema>('/api/complete-rental', data),

  getTariffs: () => apiClient.get<TariffSchema[]>('/api/tariffs'),
};
