import { apiClient } from './client';
import type { RetrieveNearestStantionsResponse } from '../types/api';

export const stantionsApi = {
  getStantions: (params?: {
    lat?: number;
    lon?: number;
    radius_meters?: number;
    limit?: number;
    offset?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params?.lat != null) qs.set('lat', String(params.lat));
    if (params?.lon != null) qs.set('lon', String(params.lon));
    if (params?.radius_meters != null) qs.set('radius_meters', String(params.radius_meters));
    if (params?.limit != null) qs.set('limit', String(params.limit));
    if (params?.offset != null) qs.set('offset', String(params.offset));
    const query = qs.toString();
    return apiClient.get<RetrieveNearestStantionsResponse>(
      `/api/stantions${query ? '?' + query : ''}`,
    );
  },
};
