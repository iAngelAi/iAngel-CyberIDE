/**
 * MetricsMonitor Component
 * 
 * Real-time visualization of Neural Core performance metrics.
 * Displays key performance indicators (KPIs) for system health monitoring.
 */

import React, { useState, useEffect } from 'react';
import { Activity, Zap, Heart } from 'lucide-react';

/**
 * Metrics summary data structure from backend
 */
interface MetricsSummary {
  transactions_per_second: number;
  average_latency_ms: number;
  error_rate: number;
  health_status: 'healthy' | 'degraded' | 'critical';
  timestamp: string;
  total_operations: number;
}

/**
 * Component props
 */
interface MetricsMonitorProps {
  pollIntervalMs?: number;
}

/**
 * Default polling interval: 5 seconds
 */
const DEFAULT_POLL_INTERVAL = 5000;

/**
 * API endpoint for metrics summary
 */
const METRICS_API_URL = 'http://localhost:8000/api/metrics/summary';

export const MetricsMonitor: React.FC<MetricsMonitorProps> = ({ 
  pollIntervalMs = DEFAULT_POLL_INTERVAL 
}) => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch metrics immediately
    const fetchMetrics = async () => {
      try {
        const response = await fetch(METRICS_API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json() as MetricsSummary;
        setMetrics(data);
        setError(null);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up polling interval
    const intervalId = setInterval(fetchMetrics, pollIntervalMs);

    // Cleanup
    return () => clearInterval(intervalId);
  }, [pollIntervalMs]);

  /**
   * Get health status color based on status
   */
  const getHealthColor = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '#10b981'; // Green
      case 'degraded':
        return '#f59e0b'; // Amber
      case 'critical':
        return '#ef4444'; // Red
      default:
        return '#6b7280'; // Gray
    }
  };

  /**
   * Get health status text with icon
   */
  const getHealthText = (status: string): string => {
    switch (status) {
      case 'healthy':
        return 'Optimal';
      case 'degraded':
        return 'Degraded';
      case 'critical':
        return 'Critical';
      default:
        return 'Unknown';
    }
  };

  /**
   * Format large numbers with K suffix
   */
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toFixed(1);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-pulse text-cyber-primary">
          Loading Neural Metrics...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-cyber-darker border border-red-500/50 rounded-lg p-4">
        <p className="text-red-400 text-center">
          ⚠ Metrics Unavailable: {error}
        </p>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-cyber-primary">
          Neural Core Performance
        </h3>
        <span className="text-xs text-white/50">
          Updated: {new Date(metrics.timestamp).toLocaleTimeString()}
        </span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Neural Load Card */}
        <div 
          className="bg-cyber-darker border border-cyber-primary/30 rounded-lg p-4 
                     hover:border-cyber-primary/50 transition-all duration-300
                     relative overflow-hidden group"
        >
          {/* Neon glow effect on hover */}
          <div className="absolute inset-0 bg-gradient-to-r from-cyber-primary/0 via-cyber-primary/10 to-cyber-primary/0 
                          opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <Zap size={24} className="text-cyber-primary" />
              <span className="text-xs text-white/60 uppercase tracking-wider">
                Neural Load
              </span>
            </div>
            
            <div className="text-3xl font-bold text-white mb-1">
              {formatNumber(metrics.transactions_per_second)}
              <span className="text-lg text-white/60 ml-1">req/s</span>
            </div>
            
            <div className="text-xs text-white/50">
              {metrics.total_operations} total operations
            </div>
          </div>
        </div>

        {/* Cognitive Latency Card */}
        <div 
          className="bg-cyber-darker border border-cyan-500/30 rounded-lg p-4 
                     hover:border-cyan-500/50 transition-all duration-300
                     relative overflow-hidden group"
        >
          {/* Neon glow effect on hover */}
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 
                          opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <Activity size={24} className="text-cyan-400" />
              <span className="text-xs text-white/60 uppercase tracking-wider">
                Cognitive Latency
              </span>
            </div>
            
            <div className="text-3xl font-bold text-white mb-1">
              {metrics.average_latency_ms.toFixed(1)}
              <span className="text-lg text-white/60 ml-1">ms</span>
            </div>
            
            <div className="text-xs text-white/50">
              Average response time
            </div>
          </div>
        </div>

        {/* Health Status Card */}
        <div 
          className="bg-cyber-darker border rounded-lg p-4 
                     hover:border-opacity-70 transition-all duration-300
                     relative overflow-hidden group"
          style={{ 
            borderColor: `${getHealthColor(metrics.health_status)}30` 
          }}
        >
          {/* Neon glow effect on hover */}
          <div 
            className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-transparent 
                       opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            style={{
              background: `linear-gradient(to right, transparent, ${getHealthColor(metrics.health_status)}10, transparent)`
            }}
          />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <Heart 
                size={24} 
                style={{ color: getHealthColor(metrics.health_status) }}
              />
              <span className="text-xs text-white/60 uppercase tracking-wider">
                System Health
              </span>
            </div>
            
            <div 
              className="text-3xl font-bold mb-1"
              style={{ color: getHealthColor(metrics.health_status) }}
            >
              {getHealthText(metrics.health_status)}
            </div>
            
            <div className="text-xs text-white/50">
              Error rate: {metrics.error_rate.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* System Status Bar */}
      <div className="bg-cyber-darker border border-cyber-dark/50 rounded-lg p-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/70">
            Neural Core Status
          </span>
          <div className="flex items-center space-x-2">
            <div 
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: getHealthColor(metrics.health_status) }}
            />
            <span 
              className="font-semibold"
              style={{ color: getHealthColor(metrics.health_status) }}
            >
              {metrics.health_status.toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
