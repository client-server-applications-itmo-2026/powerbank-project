import type { ReactNode } from 'react';
import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../../entities/auth/store';
import { ROUTES } from '../constants/routes';
import styles from './AppLayout.module.css';
import { joinStyles } from '../utils/utils';

export function AppLayout({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <button
          className={styles.hamburger}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Открыть меню"
        >
          ☰
        </button>
        <span className={styles.brand}>⚡ PowerBank</span>
        <nav className={styles.nav}>
          <NavLink
            to={ROUTES.MAP}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            Карта
          </NavLink>
          <NavLink
            to={ROUTES.RENTALS}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            Аренды
          </NavLink>
          <NavLink
            to={ROUTES.PROFILE}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            {user ? user.first_name : 'Профиль'}
          </NavLink>
        </nav>
        <button className={styles.logoutBtn} onClick={logout} title="Выйти">
          Выйти
        </button>
      </header>

      {/* Sidebar for mobile */}
      <div className={joinStyles([styles.sidebar, menuOpen && styles.sidebarOpen])}>
        <nav className={styles.sidebarNav}>
          <NavLink
            to={ROUTES.MAP}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            Карта
          </NavLink>
          <NavLink
            to={ROUTES.RENTALS}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            Аренды
          </NavLink>
          <NavLink
            to={ROUTES.PROFILE}
            className={({ isActive }) => joinStyles([styles.navLink, isActive && styles.active])}
            onClick={closeMenu}
          >
            {user ? user.first_name : 'Профиль'}
          </NavLink>
          <button className={styles.sidebarLogout} onClick={() => { logout(); closeMenu(); }}>
            Выйти
          </button>
        </nav>
      </div>

      {/* Overlay */}
      {menuOpen && <div className={styles.overlay} onClick={closeMenu} />}

      <main className={styles.main}>{children}</main>
    </div>
  );
}
