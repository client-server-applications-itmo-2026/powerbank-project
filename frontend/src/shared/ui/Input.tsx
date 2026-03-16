import type { InputHTMLAttributes } from 'react';
import styles from './Input.module.css';
import { joinStyles } from '../utils/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = '', ...props }: InputProps) {
  return (
    <div className={styles.field}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <input
        id={id}
        {...props}
        className={joinStyles([styles.input, error && styles.inputError, className])}
      />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}
