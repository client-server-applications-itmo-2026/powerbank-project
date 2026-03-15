import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../entities/auth/store';
import { ROUTES } from '../shared/constants/routes';
import { ApiError } from '../shared/api/client';
import { getApiErrorMessage } from '../shared/api/getErrorMessage';
import { Input } from '../shared/ui/Input';
import { Button } from '../shared/ui/Button';
import { Alert } from '../shared/ui/Alert';
import { useState } from 'react';
import styles from './AuthPage.module.css';

const schema = z.object({
  email: z.string().min(1, 'Введите email').email('Некорректный email'),
  password: z.string().min(1, 'Введите пароль'),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setServerError(null);
    try {
      await login(values.email, values.password);
      navigate(ROUTES.MAP, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setServerError('Неверный email или пароль');
      } else {
        setServerError(getApiErrorMessage(err, 'Произошла ошибка. Попробуйте снова.'));
      }
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⚡</div>
        <h1 className={styles.title}>Вход</h1>
        <p className={styles.subtitle}>Войдите, чтобы арендовать батарею</p>

        <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
          {serverError && <Alert type="error" message={serverError} />}

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
            id="password"
            label="Пароль"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            error={errors.password?.message}
            {...register('password')}
          />

          <Button type="submit" isLoading={isSubmitting}>
            Войти
          </Button>
        </form>

        <p className={styles.switchText}>
          Нет аккаунта?{' '}
          <Link to={ROUTES.REGISTER} className={styles.link}>
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  );
}
