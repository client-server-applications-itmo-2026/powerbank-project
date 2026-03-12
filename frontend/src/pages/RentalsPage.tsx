import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rentalsApi } from '../shared/api/rentals';
import { AppLayout } from '../shared/ui/AppLayout';
import { Alert } from '../shared/ui/Alert';
import { ROUTES } from '../shared/constants/routes';
import type { RentalSchema } from '../shared/types/api';
import styles from './RentalsPage.module.css';

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function duration(start: string, end: string | null): string {
  const ms = new Date(end ?? new Date()).getTime() - new Date(start).getTime();
  const totalMin = Math.floor(ms / 60000);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h > 0) return `${h} ч ${m} мин`;
  return `${m} мин`;
}

interface RentalCardProps {
  rental: RentalSchema;
  onComplete: (rental: RentalSchema) => void;
}

function RentalCard({ rental, onComplete }: RentalCardProps) {
  const isActive = rental.status !== 'COMPLETED' && rental.status !== 'CANCELLED';

  const statusLabel: Record<typeof rental.status, string> = {
    INITIALIZING: 'Инициализация',
    ACTIVE: 'Активна',
    WAIT_FOR_COMPLETION: 'Ожидает возврата',
    COMPLETED: 'Завершена',
    CANCELLED: 'Отменена',
  };

  return (
    <div className={[styles.card, isActive ? styles.cardActive : styles.cardDone].join(' ')}>
      <div className={styles.cardTop}>
        <div className={styles.cardId}>
          <span className={[styles.statusDot, isActive ? styles.dotActive : styles.dotDone].join(' ')} />
          Аренда #{rental.id}
        </div>
        <span className={[styles.badge, isActive ? styles.badgeActive : styles.badgeDone].join(' ')}>
          {statusLabel[rental.status]}
        </span>
      </div>

      <div className={styles.cardBody}>
        <div className={styles.infoGrid}>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Батарея</span>
            <span className={styles.infoValue}>{rental.battery_id}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Тариф</span>
            <span className={styles.infoValue}>{rental.tariff.name}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Начало</span>
            <span className={styles.infoValue}>{formatDate(rental.started_at)}</span>
          </div>
          {rental.completed_at && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Конец</span>
              <span className={styles.infoValue}>{formatDate(rental.completed_at)}</span>
            </div>
          )}
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Длительность</span>
            <span className={styles.infoValue}>
              {duration(rental.started_at, rental.completed_at)}
              {isActive && ' (идёт)'}
            </span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Станция старта</span>
            <span className={styles.infoValue}>{rental.started_at_stantion.hardware_id}</span>
          </div>
          {rental.completed_at_stantion && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Станция возврата</span>
              <span className={styles.infoValue}>{rental.completed_at_stantion.hardware_id}</span>
            </div>
          )}
          {rental.final_price != null && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Итого</span>
              <span className={[styles.infoValue, styles.price].join(' ')}>
                {rental.final_price} ₽
              </span>
            </div>
          )}
        </div>
      </div>

      {isActive && (
        <div className={styles.cardFooter}>
          <button className={styles.completeBtn} onClick={() => onComplete(rental)}>
            Завершить аренду
          </button>
        </div>
      )}
    </div>
  );
}

export function RentalsPage() {
  const navigate = useNavigate();
  const [rentals, setRentals] = useState<RentalSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRentals = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await rentalsApi.getMyRentals();
      // Show active first, then newest first for completed
      const sorted = [...res.items].sort((a, b) => {
        const aActive = a.status !== 'COMPLETED' && a.status !== 'CANCELLED';
        const bActive = b.status !== 'COMPLETED' && b.status !== 'CANCELLED';
        if (aActive && !bActive) return -1;
        if (!aActive && bActive) return 1;
        return new Date(b.started_at).getTime() - new Date(a.started_at).getTime();
      });
      setRentals(sorted);
    } catch {
      setError('Не удалось загрузить аренды');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRentals();
  }, [loadRentals]);

  const activeCount = rentals.filter(
    (r) => r.status !== 'COMPLETED' && r.status !== 'CANCELLED',
  ).length;

  function handleStartComplete(rental: RentalSchema) {
    navigate(ROUTES.MAP, { state: { completingRental: rental } });
  }

  return (
    <AppLayout>
      <div className={styles.page}>
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Мои аренды</h1>
            <p className={styles.subtitle}>
              {!loading && `${rentals.length} всего · ${activeCount} активных`}
            </p>
          </div>
          <button className={styles.refreshBtn} onClick={loadRentals} title="Обновить">
            ↻
          </button>
        </div>

        {error && <Alert type="error" message={error} />}

        {loading && (
          <div className={styles.loadingState}>
            <span className="spinner-lg" />
          </div>
        )}

        {!loading && !error && rentals.length === 0 && (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>🔋</span>
            <p className={styles.emptyTitle}>Аренд пока нет</p>
            <p className={styles.emptySubtitle}>
              Найдите ближайшую станцию на карте и возьмите батарею
            </p>
          </div>
        )}

        {!loading && rentals.length > 0 && (
          <div className={styles.list}>
            {rentals.map((rental) => (
              <RentalCard
                key={rental.id}
                rental={rental}
                onComplete={handleStartComplete}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
