import './ProgressBar.css';

interface ProgressBarProps {
  value: number; // 0–100
  variant?: 'primary' | 'success' | 'warm' | 'cool';
  size?: 'sm' | 'md';
  showLabel?: boolean;
}

export default function ProgressBar({
  value,
  variant = 'primary',
  size = 'md',
  showLabel = true,
}: ProgressBarProps) {
  const clampedValue = Math.max(0, Math.min(100, value));

  return (
    <div className={`progress-bar-wrapper progress-${size}`}>
      <div className="progress-bar-track">
        <div
          className={`progress-bar-fill progress-${variant}`}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
      {showLabel && (
        <span className="progress-bar-label">{Math.round(clampedValue)}%</span>
      )}
    </div>
  );
}
