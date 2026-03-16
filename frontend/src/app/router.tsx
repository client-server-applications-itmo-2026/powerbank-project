import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '../shared/constants/routes';
import { ProtectedRoute } from '../shared/ui/ProtectedRoute';
import { LoginPage } from '../pages/Auth/LoginPage';
import { RegisterPage } from '../pages/Auth/RegisterPage';
import { NotFoundPage } from '../pages/NotFound/NotFoundPage';
import { MapPage } from '../pages/Map/MapPage';
import { RentalsPage } from '../pages/Rental/RentalsPage';
import { ProfilePage } from '../pages/Profile/ProfilePage';

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
