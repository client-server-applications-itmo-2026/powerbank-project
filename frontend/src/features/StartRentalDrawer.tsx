import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { rentalsApi } from '../shared/api/rentals';
import { useTariffs } from '../shared/hooks/useTariffs';
import { getApiErrorMessage } from '../shared/api/getErrorMessage';
import { Button } from '../shared/ui/Button';
import { Alert } from '../shared/ui/Alert';
import type { RetrieveNearestStantionsResponseItem, RentalSchema, TariffSchema } from '../shared/types/api';
import styles from './StartRentalDrawer.module.css';
import { joinStyles } from '../shared/utils/utils';

const schema = z.object({
  tariff_id: z.string().min(1, 'Выберите тариф'),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  station: RetrieveNearestStantionsResponseItem | null;
  onClose: () => void;
  onSuccess: (rental: RentalSchema) => void;
}

export function StartRentalDrawer({ station, onClose, onSuccess }: Props) {
  const { tariffs, loading: tariffsLoading } = useTariffs();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  // Reset form when station changes
  useEffect(() => {
    reset();
    setServerError(null);
  }, [station, reset]);

  async function onSubmit(values: FormValues) {
    if (!station) return;
    setServerError(null);
    try {
      const rental = await rentalsApi.startRental({
        stantion_id: station.hardware_id,
        tariff_id: Number(values.tariff_id),
      });
      onSuccess(rental);
    } catch (err) {
      setServerError(getApiErrorMessage(err, 'Не удалось начать аренду'));
    }
  }

  const open = station !== null;

  return (
    <>
      {open && <div className={styles.overlay} onClick={onClose} />}
      <div className={joinStyles([styles.drawer, open && styles.drawerOpen])}>
        <div className={styles.handle} />

        {station && (
          <>
            <div className={styles.drawerHeader}>
              <h2 className={styles.drawerTitle}>Начать аренду</h2>
              <button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
                ✕
              </button>
            </div>

            <div className={styles.stationInfo}>
              <div className={styles.stationRow}>
                <span className={styles.stationLabel}>Станция</span>
                <span className={styles.stationValue}>{station.hardware_id}</span>
              </div>
              <div className={styles.stationRow}>
                <span className={styles.stationLabel}>Батареи</span>
                <span
                  className={joinStyles([
                    styles.stationValue,
                    station.available_batteries > 0 ? styles.available : styles.unavailable,
                  ])}
                >
                  {station.available_batteries} доступно
                </span>
              </div>
              <div className={styles.stationRow}>
                <span className={styles.stationLabel}>Свободных слотов</span>
                <span className={styles.stationValue}>{station.free_slots}</span>
              </div>
            </div>

            {station.available_batteries === 0 ? (
              <Alert type="info" message="На этой станции нет доступных батарей" />
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
                {serverError && <Alert type="error" message={serverError} />}

                <div className={styles.field}>
                  <label className={styles.label}>Тариф</label>
                  {tariffsLoading ? (
                    <div className={styles.tariffLoading}>Загрузка тарифов…</div>
                  ) : (
                    <div className={styles.tariffList}>
                      {tariffs.map((t: TariffSchema) => (
                        <label key={t.id} className={styles.tariffCard}>
                          <input
                            type="radio"
                            value={t.id}
                            className={styles.tariffRadio}
                            {...register('tariff_id')}
                          />
                          <div className={styles.tariffInfo}>
                            <span className={styles.tariffName}>{t.name}</span>
                            {t.price_per_tick != null && (
                              <span className={styles.tariffPrice}>
                                {t.price_per_tick} ₽/мин
                              </span>
                            )}
                            <span className={styles.tariffDesc}>{t.description}</span>
                          </div>
                        </label>
                      ))}
                      {tariffs.length === 0 && (
                        <p className={styles.noTariffs}>Нет доступных тарифов</p>
                      )}
                    </div>
                  )}
                  {errors.tariff_id && (
                    <span className={styles.fieldError}>{errors.tariff_id.message}</span>
                  )}
                </div>

                <Button
                  type="submit"
                  isLoading={isSubmitting}
                  disabled={tariffsLoading || tariffs.length === 0}
                >
                  Взять батарею
                </Button>
              </form>
            )}
          </>
        )}
      </div>
    </>
  );
}
