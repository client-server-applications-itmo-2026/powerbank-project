import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '../shared/constants/routes';
import { ProtectedRoute } from '../shared/ui/ProtectedRoute';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { MapPage } from '../pages/MapPage';
import { RentalsPage } from '../pages/RentalsPage';

// Placeholder pages for routes not yet implemented
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
      <h2>{title}</h2>
      <p>This page is coming soon.</p>
    </div>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

        {/* Protected */}
        <Route element={<ProtectedRoute />}>
          <Route path={ROUTES.MAP} element={<MapPage />} />
          <Route path={ROUTES.RENTALS} element={<RentalsPage />} />
          <Route path={ROUTES.PROFILE} element={<PlaceholderPage title="Профиль" />} />
        </Route>

        {/* Root redirect */}
        <Route path={ROUTES.ROOT} element={<Navigate to={ROUTES.MAP} replace />} />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
