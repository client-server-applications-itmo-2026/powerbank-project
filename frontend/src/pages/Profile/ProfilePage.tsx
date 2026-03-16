import { useCallback, useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AppLayout } from '../../shared/ui/AppLayout';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';
import { Alert } from '../../shared/ui/Alert';
import { usersApi } from '../../shared/api/users';
import { useAuthStore } from '../../entities/auth/store';
import { ApiError } from '../../shared/api/client';
import type { UserRetrieveResponse } from '../../shared/types/api';
import styles from './ProfilePage.module.css';

/** Resolve avatar URL for img src. When using Vite proxy (no VITE_API_BASE_URL), use pathname so /media is proxied; otherwise use full URL or prepend base for relative paths. */
function getAvatarSrc(avatarUrl: string | null): string | null {
  if (!avatarUrl) return null;
  const base = import.meta.env.VITE_API_BASE_URL ?? '';
  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://')) {
    if (!base) return new URL(avatarUrl).pathname;
    return avatarUrl;
  }
  return base ? `${base.replace(/\/$/, '')}${avatarUrl}` : avatarUrl;
}

const editProfileSchema = z.object({
  first_name: z.string().min(1, 'Введите имя'),
  last_name: z.string().min(1, 'Введите фамилию'),
  patronymic_name: z.string().optional(),
  email: z.string().min(1, 'Введите email').email('Некорректный email'),
  phone_number: z.string().optional(),
});

type EditProfileFormValues = z.infer<typeof editProfileSchema>;

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

interface EditProfileModalProps {
  user: UserRetrieveResponse;
  onClose: () => void;
  onSaved: (updated: UserRetrieveResponse) => void;
}

function EditProfileModal({ user, onClose, onSaved }: EditProfileModalProps) {
  const [serverError, setServerError] = useState<string | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(user.avatar_url);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    };
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EditProfileFormValues>({
    resolver: zodResolver(editProfileSchema),
    defaultValues: {
      first_name: user.first_name,
      last_name: user.last_name,
      patronymic_name: user.patronymic_name ?? '',
      email: user.email,
      phone_number: user.phone_number ?? '',
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    if (file) {
      setAvatarFile(file);
      const url = URL.createObjectURL(file);
      objectUrlRef.current = url;
      setAvatarPreview(url);
    } else {
      setAvatarFile(null);
      setAvatarPreview(user.avatar_url);
    }
  };

  async function onSubmit(values: EditProfileFormValues) {
    setServerError(null);
    try {
      if (avatarFile) {
        await usersApi.uploadAvatar(avatarFile);
      }
      const updated = await usersApi.updateMe({
        first_name: values.first_name,
        last_name: values.last_name,
        patronymic_name: values.patronymic_name || null,
        email: values.email,
        phone_number: values.phone_number || null,
      });
      onSaved(updated);
      onClose();
    } catch (err) {
      if (err instanceof ApiError) {
        const data = err.data as Record<string, unknown>;
        const detail =
          typeof data?.detail === 'string'
            ? data.detail
            : 'Не удалось сохранить профиль. Проверьте данные.';
        setServerError(detail);
      } else {
        setServerError('Произошла ошибка. Попробуйте снова.');
      }
    }
  }

  return (
    <div className={styles.overlay} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Редактировать профиль</h2>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Закрыть"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
          {serverError && <Alert type="error" message={serverError} />}

          <div className={styles.avatarField}>
            <label className={styles.infoLabel}>Аватар</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {avatarPreview ? (
                <img
                  src={avatarPreview.startsWith('blob:') ? avatarPreview : (getAvatarSrc(avatarPreview) ?? avatarPreview)}
                  alt=""
                  className={styles.avatarPreview}
                />
              ) : (
                <div className={styles.avatarPreviewEmpty}>?</div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className={styles.fileInput}
              />
            </div>
          </div>

          <div className={styles.row}>
            <Input
              id="last_name"
              label="Фамилия"
              placeholder="Иванов"
              autoComplete="family-name"
              error={errors.last_name?.message}
              {...register('last_name')}
            />
            <Input
              id="first_name"
              label="Имя"
              placeholder="Иван"
              autoComplete="given-name"
              error={errors.first_name?.message}
              {...register('first_name')}
            />
          </div>

          <Input
            id="patronymic_name"
            label="Отчество (необязательно)"
            placeholder="Иванович"
            autoComplete="additional-name"
            error={errors.patronymic_name?.message}
            {...register('patronymic_name')}
          />

          <Input
            id="email"
            label="Email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            error={errors.email?.message}
            {...register('email')}
          />

          <Input
            id="phone_number"
            label="Телефон (необязательно)"
            type="tel"
            placeholder="+7 999 000 00 00"
            autoComplete="tel"
            error={errors.phone_number?.message}
            {...register('phone_number')}
          />

          <div className={styles.modalActions}>
            <Button type="button" variant="secondary" onClick={onClose}>
              Отменить
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Сохранить
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function ProfilePage() {
  const setUser = useAuthStore((s) => s.setUser);
  const [profile, setProfile] = useState<UserRetrieveResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editOpen, setEditOpen] = useState(false);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const user = await usersApi.getMe();
      setProfile(user);
    } catch {
      setError('Не удалось загрузить профиль');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  function handleProfileSaved(updated: UserRetrieveResponse) {
    setProfile(updated);
    setUser(updated);
  }

  if (loading) {
    return (
      <AppLayout>
        <div className={styles.page}>
          <div className={styles.loadingState}>
            <span className="spinner-lg" />
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error || !profile) {
    return (
      <AppLayout>
        <div className={styles.page}>
          {error && <Alert type="error" message={error} />}
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className={styles.page}>
        <div className={styles.header}>
          <h1 className={styles.title}>Профиль</h1>
          <p className={styles.subtitle}>Ваши данные для аренды</p>
        </div>

        <div className={styles.card}>
          <div className={styles.avatarWrap}>
            {profile.avatar_url ? (
              <img
                src={getAvatarSrc(profile.avatar_url) ?? profile.avatar_url}
                alt=""
                className={styles.avatar}
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  const next = e.currentTarget.nextElementSibling as HTMLElement | null;
                  if (next) next.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className={styles.avatarPlaceholder}
              style={{ display: profile.avatar_url ? 'none' : 'flex' }}
            >
              👤
            </div>
          </div>

          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Имя</span>
              <span className={styles.infoValue}>
                {profile.first_name || <span className={styles.infoValueEmpty}>—</span>}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Фамилия</span>
              <span className={styles.infoValue}>
                {profile.last_name || <span className={styles.infoValueEmpty}>—</span>}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Отчество</span>
              <span className={styles.infoValue}>
                {profile.patronymic_name || <span className={styles.infoValueEmpty}>—</span>}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Email</span>
              <span className={styles.infoValue}>{profile.email}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Телефон</span>
              <span className={styles.infoValue}>
                {profile.phone_number || <span className={styles.infoValueEmpty}>—</span>}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Дата регистрации</span>
              <span className={styles.infoValue}>{formatDate(profile.date_joined)}</span>
            </div>
          </div>

          <div className={styles.cardFooter}>
            <button
              type="button"
              className={styles.editBtn}
              onClick={() => setEditOpen(true)}
            >
              Редактировать профиль
            </button>
          </div>
        </div>

        {editOpen && (
          <EditProfileModal
            user={profile}
            onClose={() => setEditOpen(false)}
            onSaved={handleProfileSaved}
          />
        )}
      </div>
    </AppLayout>
  );
}
