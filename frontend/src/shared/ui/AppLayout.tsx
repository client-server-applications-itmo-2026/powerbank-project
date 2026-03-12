import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../../entities/auth/store';
import { ROUTES } from '../constants/routes';
import styles from './AppLayout.module.css';

export function AppLayout({ children }: { children: React.ReactNode }) {
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <span className={styles.brand}>⚡ PowerBank</span>
        <nav className={styles.nav}>
          <NavLink
            to={ROUTES.MAP}
            className={({ isActive }) => [styles.navLink, isActive ? styles.active : ''].join(' ')}
          >
            Карта
          </NavLink>
          <NavLink
            to={ROUTES.RENTALS}
            className={({ isActive }) => [styles.navLink, isActive ? styles.active : ''].join(' ')}
          >
            Аренды
          </NavLink>
          <NavLink
            to={ROUTES.PROFILE}
            className={({ isActive }) => [styles.navLink, isActive ? styles.active : ''].join(' ')}
          >
            {user ? user.first_name : 'Профиль'}
          </NavLink>
        </nav>
        <button className={styles.logoutBtn} onClick={logout} title="Выйти">
          Выйти
        </button>
      </header>
      <main className={styles.main}>{children}</main>
    </div>
  );
}
