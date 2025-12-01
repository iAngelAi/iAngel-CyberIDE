import type { DiagnosticAlert } from '../../types';
import { AlertTriangle, XCircle, Info, AlertOctagon, X } from 'lucide-react';

interface AlertOverlayProps {
  alerts: DiagnosticAlert[];
  onDismiss?: (alertId: string) => void;
  onResolve?: (alertId: string) => void;
}

/**
 * AlertOverlay - Diagnostic alerts visualization
 *
 * Displays critical, error, warning, and info alerts
 * in the cyberpunk aesthetic with appropriate colors.
 */
export const AlertOverlay: React.FC<AlertOverlayProps> = ({
  alerts,
  onDismiss,
  onResolve,
}) => {
  const activeAlerts = alerts.filter((alert) => !alert.resolved);

  if (activeAlerts.length === 0) return null;

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-2xl w-full px-4">
      <div className="space-y-3">
        {activeAlerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onDismiss={onDismiss}
            onResolve={onResolve}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * Individual Alert Card
 */
interface AlertCardProps {
  alert: DiagnosticAlert;
  onDismiss?: (alertId: string) => void;
  onResolve?: (alertId: string) => void;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert, onDismiss, onResolve }) => {
  const config = getAlertConfig(alert.severity);

  return (
    <div
      className={`
        bg-cyber-dark/95 backdrop-blur-sm rounded-lg p-4
        border-2 ${config.borderColor}
        shadow-lg animate-pulse-slow
      `}
      style={{
        boxShadow: `0 0 20px ${config.glowColor}`,
      }}
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className={`flex-shrink-0 ${config.iconColor}`}>
          {config.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-mono font-bold ${config.textColor}`}>
                {config.label}
              </span>
              <span className="text-xs text-white/40 font-mono">
                {alert.region}
              </span>
            </div>
            <button
              onClick={() => onDismiss?.(alert.id)}
              className="text-white/40 hover:text-white transition-colors"
              aria-label="Dismiss alert"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Message */}
          <p className={`text-sm font-medium mb-2 ${config.textColor}`}>
            {alert.message}
          </p>

          {/* Details */}
          <p className="text-xs text-white/60 font-mono mb-3">
            {alert.details}
          </p>

          {/* Timestamp */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-white/40 font-mono">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </span>

            {/* Actions */}
            {onResolve && alert.severity !== 'info' && (
              <button
                onClick={() => onResolve(alert.id)}
                className={`
                  text-xs font-mono px-3 py-1 rounded
                  ${config.buttonClass}
                  transition-all duration-200
                `}
              >
                RESOLVE
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Get visual configuration based on severity
 */
function getAlertConfig(severity: DiagnosticAlert['severity']) {
  switch (severity) {
    case 'critical':
      return {
        icon: <AlertOctagon className="w-6 h-6" />,
        label: 'CRITICAL',
        iconColor: 'text-red-500',
        textColor: 'text-red-400',
        borderColor: 'border-red-500',
        glowColor: 'rgba(239, 68, 68, 0.5)',
        buttonClass:
          'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500 hover:text-white',
      };
    case 'error':
      return {
        icon: <XCircle className="w-6 h-6" />,
        label: 'ERROR',
        iconColor: 'text-neural-error',
        textColor: 'text-neural-error',
        borderColor: 'border-neural-error',
        glowColor: 'rgba(255, 0, 85, 0.4)',
        buttonClass:
          'bg-neural-error/20 text-neural-error border border-neural-error/50 hover:bg-neural-error hover:text-white',
      };
    case 'warning':
      return {
        icon: <AlertTriangle className="w-6 h-6" />,
        label: 'CAUTION',
        iconColor: 'text-neural-warning',
        textColor: 'text-neural-warning',
        borderColor: 'border-neural-warning',
        glowColor: 'rgba(255, 165, 0, 0.4)',
        buttonClass:
          'bg-neural-warning/20 text-neural-warning border border-neural-warning/50 hover:bg-neural-warning hover:text-cyber-dark',
      };
    case 'info':
    default:
      return {
        icon: <Info className="w-6 h-6" />,
        label: 'INFO',
        iconColor: 'text-cyber-primary',
        textColor: 'text-cyber-primary',
        borderColor: 'border-cyber-primary',
        glowColor: 'rgba(0, 240, 255, 0.3)',
        buttonClass:
          'bg-cyber-primary/20 text-cyber-primary border border-cyber-primary/50 hover:bg-cyber-primary hover:text-cyber-dark',
      };
  }
}
