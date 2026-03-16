import { Link } from 'react-router-dom';
import { ROUTES } from '../../shared/constants/routes';
import styles from './NotFoundPage.module.css';

export function NotFoundPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.code}>404</h1>
      <p className={styles.message}>Страница не найдена</p>
      <Link to={ROUTES.ROOT} className={styles.link}>
        На главную
      </Link>
    </div>
  );
}
