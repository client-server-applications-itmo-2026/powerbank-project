import { useEffect } from 'react';
import { useAuthStore } from '../entities/auth/store';
import { AppRouter } from './router';

export function App() {
  const restoreSession = useAuthStore((s) => s.restoreSession);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  return <AppRouter />;
}
