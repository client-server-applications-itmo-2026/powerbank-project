import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../entities/auth/store';
import { ROUTES } from '../constants/routes';

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
        <span className="spinner-lg" />
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to={ROUTES.LOGIN} replace />;
}
