import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '../shared/constants/routes';
import { ProtectedRoute } from '../shared/ui/ProtectedRoute';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { MapPage } from '../pages/MapPage';
import { RentalsPage } from '../pages/RentalsPage';
import { ProfilePage } from '../pages/ProfilePage';

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
          <Route path={ROUTES.PROFILE} element={<ProfilePage />} />
        </Route>

        {/* Root redirect */}
        <Route path={ROUTES.ROOT} element={<Navigate to={ROUTES.MAP} replace />} />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
