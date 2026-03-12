import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { rentalsApi } from '../shared/api/rentals';
import { useRentalPolling } from '../shared/hooks/useRentalPolling';
import { ApiError } from '../shared/api/client';
import { Button } from '../shared/ui/Button';
import { Alert } from '../shared/ui/Alert';
import type { RentalSchema } from '../shared/types/api';
import styles from './CompleteRentalFlow.module.css';

// ─── Steps ────────────────────────────────────────────────────────────────────
// 1. SELECT_STATION  – user picks return station, submits → POST /api/complete-rental
// 2. WAIT_FOR_COMPLETION – polling until status === 'COMPLETED'
// 3. COMPLETED        – success screen
type Step = 'SELECT_STATION' | 'WAIT_FOR_COMPLETION' | 'COMPLETED';

const schema = z.object({
  stantion_id: z.string().min(1, 'Введите ID станции'),
});
type FormValues = z.infer<typeof schema>;

interface Props {
  rental: RentalSchema;
  /** When provided, skips the manual ID input and shows a station-confirmation view. */
  preselectedStantionId?: string;
  onClose: () => void;
  onCompleted: (updated: RentalSchema) => void;
}

export function CompleteRentalFlow({ rental, preselectedStantionId, onClose, onCompleted }: Props) {
  const [step, setStep] = useState<Step>('SELECT_STATION');
  const [pollingRentalId, setPollingRentalId] = useState<number | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);

  const { rental: polledRental, completed, error: pollError } = useRentalPolling({
    rentalId: pollingRentalId,
  });

  // When polling detects completion — advance to final step
  if (step === 'WAIT_FOR_COMPLETION' && completed && polledRental) {
    // Use a microtask to avoid setState during render
    Promise.resolve().then(() => {
      setStep('COMPLETED');
      onCompleted(polledRental);
    });
  }

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setServerError(null);
    try {
      const updated = await rentalsApi.completeRental({
        rental_id: rental.id,
        stantion_id: values.stantion_id,
      });
      // If backend already returns COMPLETED status, skip polling
      if (updated.status === 'COMPLETED') {
        setStep('COMPLETED');
        onCompleted(updated);
      } else {
        setPollingRentalId(rental.id);
        setStep('WAIT_FOR_COMPLETION');
      }
    } catch (err) {
      if (err instanceof ApiError) {
        const data = err.data as Record<string, unknown>;
        setServerError(
          typeof data?.detail === 'string' ? data.detail : 'Не удалось завершить аренду',
        );
      } else {
        setServerError('Произошла ошибка. Попробуйте снова.');
      }
    }
  }

  async function handleConfirmPreselected() {
    setServerError(null);
    setIsConfirming(true);
    try {
      const updated = await rentalsApi.completeRental({
        rental_id: rental.id,
        stantion_id: preselectedStantionId!,
      });
      if (updated.status === 'COMPLETED') {
        setStep('COMPLETED');
        onCompleted(updated);
      } else {
        setPollingRentalId(rental.id);
        setStep('WAIT_FOR_COMPLETION');
      }
    } catch (err) {
      if (err instanceof ApiError) {
        const data = err.data as Record<string, unknown>;
        setServerError(
          typeof data?.detail === 'string' ? data.detail : 'Не удалось завершить аренду',
        );
      } else {
        setServerError('Произошла ошибка. Попробуйте снова.');
      }
      setIsConfirming(false);
    }
  }

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal}>
        {/* ── Step 1: select return station ── */}
        {step === 'SELECT_STATION' && (
          <>
            <div className={styles.header}>
              <h2 className={styles.title}>Завершение аренды</h2>
              <button className={styles.closeBtn} onClick={onClose}>✕</button>
            </div>

            <div className={styles.rentalMeta}>
              <div className={styles.metaRow}>
                <span className={styles.metaLabel}>Аренда</span>
                <span className={styles.metaValue}>#{rental.id}</span>
              </div>
              <div className={styles.metaRow}>
                <span className={styles.metaLabel}>Батарея</span>
                <span className={styles.metaValue}>{rental.battery_id}</span>
              </div>
              <div className={styles.metaRow}>
                <span className={styles.metaLabel}>Тариф</span>
                <span className={styles.metaValue}>{rental.tariff.name}</span>
              </div>
            </div>

            {preselectedStantionId ? (
              // Station was selected on the map — show confirmation
              <>
                <p className={styles.description}>
                  Вставьте батарею в слот выбранной станции и подтвердите возврат.
                </p>
                <div className={styles.stationConfirmBox}>
                  <span className={styles.stationConfirmLabel}>Станция возврата</span>
                  <span className={styles.stationConfirmId}>📍 {preselectedStantionId}</span>
                </div>
                {serverError && <Alert type="error" message={serverError} />}
                <div className={styles.actions}>
                  <Button variant="secondary" type="button" onClick={onClose}>
                    Отмена
                  </Button>
                  <Button isLoading={isConfirming} onClick={handleConfirmPreselected}>
                    Подтвердить возврат
                  </Button>
                </div>
              </>
            ) : (
              // Manual ID input
              <>
                <p className={styles.description}>
                  Выберите станцию, на которую хотите вернуть батарею.
                </p>
                <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
                  {serverError && <Alert type="error" message={serverError} />}

                  <div className={styles.field}>
                    <label className={styles.label}>ID станции возврата</label>
                    <input
                      className={[styles.input, errors.stantion_id ? styles.inputError : ''].join(' ')}
                      placeholder="Например: STATION-001"
                      {...register('stantion_id')}
                    />
                    {errors.stantion_id && (
                      <span className={styles.fieldError}>{errors.stantion_id.message}</span>
                    )}
                  </div>

                  <div className={styles.actions}>
                    <Button variant="secondary" type="button" onClick={onClose}>
                      Отмена
                    </Button>
                    <Button type="submit" isLoading={isSubmitting}>
                      Сдать батарею
                    </Button>
                  </div>
                </form>
              </>
            )}
          </>
        )}

        {/* ── Step 2: waiting for completion ── */}
        {step === 'WAIT_FOR_COMPLETION' && (
          <>
            <div className={styles.header}>
              <h2 className={styles.title}>Вставьте батарею</h2>
            </div>

            <div className={styles.waitContent}>
              <div className={styles.batteryAnim}>🔋</div>
              <p className={styles.waitTitle}>Вставьте аккумулятор в слот станции</p>
              <p className={styles.waitSubtitle}>
                Ожидаем подтверждение от станции…
              </p>
              <div className={styles.pollingDots}>
                <span />
                <span />
                <span />
              </div>
              {pollError && <Alert type="error" message={pollError} />}
            </div>
          </>
        )}

        {/* ── Step 3: success ── */}
        {step === 'COMPLETED' && (
          <>
            <div className={styles.header}>
              <h2 className={styles.title}>Аренда завершена</h2>
            </div>

            <div className={styles.successContent}>
              <div className={styles.successIcon}>✅</div>
              <p className={styles.successTitle}>Батарея успешно возвращена!</p>

              {polledRental && polledRental.final_price != null && (
                <div className={styles.finalPrice}>
                  Итого: <strong>{polledRental.final_price} ₽</strong>
                </div>
              )}

              <div className={styles.successMeta}>
                {polledRental?.completed_at && (
                  <div className={styles.metaRow}>
                    <span className={styles.metaLabel}>Завершена</span>
                    <span className={styles.metaValue}>
                      {new Date(polledRental.completed_at).toLocaleString('ru-RU')}
                    </span>
                  </div>
                )}
                {polledRental?.completed_at_stantion && (
                  <div className={styles.metaRow}>
                    <span className={styles.metaLabel}>Возврат на</span>
                    <span className={styles.metaValue}>
                      {polledRental.completed_at_stantion.hardware_id}
                    </span>
                  </div>
                )}
              </div>

              <Button onClick={onClose}>Закрыть</Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
