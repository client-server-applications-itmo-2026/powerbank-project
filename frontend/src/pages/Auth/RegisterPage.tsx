import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { usersApi } from '../../shared/api/users';
import { useAuthStore } from '../../entities/auth/store';
import { ROUTES } from '../../shared/constants/routes';
import { ApiError } from '../../shared/api/client';
import { getApiErrorMessage } from '../../shared/api/getErrorMessage';
import { Input } from '../../shared/ui/Input';
import { Button } from '../../shared/ui/Button';
import { Alert } from '../../shared/ui/Alert';
import styles from './LoginPage.module.css';
import { joinStyles } from '../../shared/utils/utils';

const schema = z
  .object({
    email: z.string().min(1, 'Введите email').email('Некорректный email'),
    first_name: z.string().min(1, 'Введите имя'),
    last_name: z.string().min(1, 'Введите фамилию'),
    patronymic_name: z.string().optional(),
    phone_number: z.string().optional(),
    password: z.string().min(6, 'Пароль — минимум 6 символов'),
    re_password: z.string().min(1, 'Подтвердите пароль'),
  })
  .refine((d) => d.password === d.re_password, {
    message: 'Пароли не совпадают',
    path: ['re_password'],
  });

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
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
      await usersApi.register({
        email: values.email,
        password: values.password,
        re_password: values.re_password,
        first_name: values.first_name,
        last_name: values.last_name,
        patronymic_name: values.patronymic_name ?? null,
        phone_number: values.phone_number ?? null,
      });
      // Auto-login after successful registration
      await login(values.email, values.password);
      navigate(ROUTES.MAP, { replace: true });
    } catch (err) {
      setServerError(
        getApiErrorMessage(err, 'Ошибка регистрации. Проверьте данные и попробуйте снова.'),
      );
    }
  }

  return (
    <div className={styles.page}>
      <div className={joinStyles([styles.card, styles.cardWide])}>
        <div className={styles.logo}>⚡</div>
        <h1 className={styles.title}>Регистрация</h1>
        <p className={styles.subtitle}>Создайте аккаунт для аренды батареи</p>

        <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
          {serverError && <Alert type="error" message={serverError} />}

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

          <Input
            id="password"
            label="Пароль"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            error={errors.password?.message}
            {...register('password')}
          />

          <Input
            id="re_password"
            label="Подтвердите пароль"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            error={errors.re_password?.message}
            {...register('re_password')}
          />

          <Button type="submit" isLoading={isSubmitting}>
            Зарегистрироваться
          </Button>
        </form>

        <p className={styles.switchText}>
          Уже есть аккаунт?{' '}
          <Link to={ROUTES.LOGIN} className={styles.link}>
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
}
