import { useCallback, useEffect, useRef, useState } from 'react';
import { rentalsApi } from '../api/rentals';
import type { RentalSchema } from '../types/api';

function isCompleted(rental: RentalSchema): boolean {
  return rental.status === 'COMPLETED';
}

interface UseRentalPollingOptions {
  rentalId: number | null;
  intervalMs?: number;
}

interface UseRentalPollingResult {
  rental: RentalSchema | null;
  completed: boolean;
  error: string | null;
  polling: boolean;
}

export function useRentalPolling({
  rentalId,
  intervalMs = 3000,
}: UseRentalPollingOptions): UseRentalPollingResult {
  const [rental, setRental] = useState<RentalSchema | null>(null);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stopRef = useRef(false);

  const clearTimer = useCallback(() => {
    if (timerRef.current != null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const poll = useCallback(async () => {
    if (rentalId == null || stopRef.current) return;

    setPolling(true);
    try {
      const data = await rentalsApi.getRentalById(rentalId);
      setRental(data);
      if (isCompleted(data)) {
        setCompleted(true);
        setPolling(false);
        stopRef.current = true;
        return;
      }
    } catch {
      setError('Не удалось получить статус аренды');
      setPolling(false);
      stopRef.current = true;
      return;
    }

    // Schedule next poll
    timerRef.current = setTimeout(() => {
      void poll();
    }, intervalMs);
  }, [rentalId, intervalMs]);

  useEffect(() => {
    if (rentalId == null) return;

    stopRef.current = false;
    setCompleted(false);
    setRental(null);
    setError(null);

    void poll();

    return () => {
      stopRef.current = true;
      clearTimer();
    };
  }, [rentalId, poll, clearTimer]);

  return { rental, completed, error, polling };
}
