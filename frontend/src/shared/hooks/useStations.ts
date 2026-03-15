import { useCallback, useEffect, useState } from 'react';
import { stantionsApi } from '../api/stantions';
import { getApiErrorMessage } from '../api/getErrorMessage';
import type { RetrieveNearestStantionsResponseItem } from '../types/api';

interface UseStationsOptions {
  lat?: number | null;
  lon?: number | null;
  radius_meters?: number;
  enabled?: boolean;
}

interface UseStationsResult {
  stations: RetrieveNearestStantionsResponseItem[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStations({
  lat,
  lon,
  radius_meters = 5000,
  enabled = true,
}: UseStationsOptions): UseStationsResult {
  const [stations, setStations] = useState<RetrieveNearestStantionsResponseItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    setError(null);
    try {
      const res = await stantionsApi.getStantions({
        lat: lat ?? undefined,
        lon: lon ?? undefined,
        radius_meters,
      });
      setStations(res.results);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Не удалось загрузить станции'));
    } finally {
      setLoading(false);
    }
  }, [lat, lon, radius_meters, enabled]);

  useEffect(() => {
    void fetch();
  }, [fetch]);

  return { stations, loading, error, refetch: fetch };
}
