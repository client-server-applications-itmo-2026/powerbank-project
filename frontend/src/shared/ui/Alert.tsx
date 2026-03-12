import styles from './Alert.module.css';

interface AlertProps {
  type: 'error' | 'success' | 'info';
  message: string;
}

export function Alert({ type, message }: AlertProps) {
  return (
    <div className={[styles.alert, styles[type]].join(' ')} role="alert">
      {message}
    </div>
  );
}
