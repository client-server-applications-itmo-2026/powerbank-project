import { useEffect, useState } from 'react';
import { rentalsApi } from '../api/rentals';
import { getApiErrorMessage } from '../api/getErrorMessage';
import type { TariffSchema } from '../types/api';

export function useTariffs() {
  const [tariffs, setTariffs] = useState<TariffSchema[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    rentalsApi
      .getTariffs()
      .then((data) => setTariffs(data.filter((t) => t.is_active)))
      .catch((err) => setError(getApiErrorMessage(err, 'Не удалось загрузить тарифы')))
      .finally(() => setLoading(false));
  }, []);

  return { tariffs, loading, error };
}
