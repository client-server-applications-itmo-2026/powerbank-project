import type { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';
import { joinStyles } from '../utils/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
}

export function Button({
  children,
  variant = 'primary',
  isLoading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={joinStyles([styles.btn, styles[variant], className])}
    >
      {isLoading ? <span className={styles.spinner} /> : children}
    </button>
  );
}
