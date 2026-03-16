import { joinStyles } from '../utils/utils';
import styles from './Alert.module.css';

interface AlertProps {
  type: 'error' | 'success' | 'info';
  message: string;
}

export function Alert({ type, message }: AlertProps) {
  return (
    <div className={joinStyles([styles.alert, styles[type]])} role="alert">
      {message}
    </div>
  );
}
