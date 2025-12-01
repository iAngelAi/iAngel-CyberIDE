/**
 * Brain Helpers - Utility functions for Neural Core calculations
 */

import type { NeuralRegion, ProjectMetrics, HealthStatus } from '../types';

/**
 * Calculate overall illumination level based on project metrics
 * @param metrics - Current project metrics
 * @returns Illumination level (0-1)
 */
export function calculateIllumination(metrics: ProjectMetrics): number {
  const weights = {
    tests: 0.3,
    modules: 0.25,
    documentation: 0.15,
    integrations: 0.2,
    license: 0.1,
  };

  let totalIllumination = 0;

  // Test coverage contribution
  totalIllumination += (metrics.tests.coverage / 100) * weights.tests;

  // Module completion contribution
  const moduleProgress =
    metrics.coreModules.total > 0
      ? metrics.coreModules.completed / metrics.coreModules.total
      : 0;
  totalIllumination += moduleProgress * weights.modules;

  // Documentation contribution
  const docProgress =
    metrics.documentation.filesTotal > 0
      ? metrics.documentation.filesUpToDate / metrics.documentation.filesTotal
      : 0;
  totalIllumination += docProgress * weights.documentation;

  // Integration contribution
  const integrationProgress =
    metrics.integrations.required > 0
      ? metrics.integrations.validated / metrics.integrations.required
      : 1; // If no integrations required, consider it complete
  totalIllumination += integrationProgress * weights.integrations;

  // License contribution
  const licenseProgress =
    metrics.license.required && metrics.license.valid ? 1 : metrics.license.required ? 0 : 1;
  totalIllumination += licenseProgress * weights.license;

  return Math.min(1, Math.max(0, totalIllumination));
}

/**
 * Determine health status based on metrics
 * @param metrics - Current project metrics
 * @returns Health status
 */
export function determineHealthStatus(metrics: ProjectMetrics): HealthStatus {
  const illumination = calculateIllumination(metrics);

  // First determine base health status from illumination level
  let status: HealthStatus;
  if (illumination === 0) {
    status = 'offline';
  } else if (illumination >= 0.90) {
    status = 'optimal';
  } else if (illumination >= 0.70) {
    status = 'healthy';
  } else if (illumination >= 0.40) {
    status = 'warning';
  } else {
    status = 'critical'; // illumination > 0 but < 0.40
  }

  // Override with critical status for severe failures
  // (only applies when status is optimal or healthy - failures mask good metrics)
  if (status === 'optimal' || status === 'healthy') {
    // Multiple core module failures (>1) indicate critical system issues
    if (metrics.coreModules.failed > 1) {
      return 'critical';
    }

    // Test failure rate above 30% indicates critical quality issues
    if (metrics.tests.total > 0 && metrics.tests.failed > metrics.tests.total * 0.3) {
      return 'critical';
    }
  }

  return status;
}

/**
 * Generate neural regions from project structure
 * @param metrics - Project metrics
 * @returns Array of neural regions
 */
export function generateNeuralRegions(metrics: ProjectMetrics): NeuralRegion[] {
  const regions: NeuralRegion[] = [];

  // Core Logic region
  const coreProgress =
    metrics.coreModules.total > 0
      ? (metrics.coreModules.completed / metrics.coreModules.total) * 100
      : 0;
  regions.push({
    id: 'core-logic',
    name: 'Core Logic',
    position: [2, 1, 0],
    status: getRegionStatus(coreProgress, metrics.coreModules.failed),
    progress: coreProgress,
    illumination: coreProgress / 100,
  });

  // API Integration region
  const apiProgress =
    metrics.integrations.required > 0
      ? (metrics.integrations.validated / metrics.integrations.required) * 100
      : 100;
  regions.push({
    id: 'api-integration',
    name: 'API Integration',
    position: [1.5, -1, 1.5],
    status: getRegionStatus(apiProgress, 0),
    progress: apiProgress,
    illumination: apiProgress / 100,
  });

  // Tests region
  const testProgress = metrics.tests.coverage;
  // Tests use percentage-based failure detection (handled at overall health level)
  // Only mark critical if test failure rate is catastrophic (>30%)
  const testCriticalFailures = metrics.tests.total > 0 && metrics.tests.failed > metrics.tests.total * 0.3
    ? 2 // Mark as critical
    : 0; // Otherwise use progress-based status
  regions.push({
    id: 'tests',
    name: 'Tests',
    position: [0, 2, -1],
    status: getRegionStatus(testProgress, testCriticalFailures),
    progress: testProgress,
    illumination: testProgress / 100,
  });

  // Documentation region
  const docProgress =
    metrics.documentation.filesTotal > 0
      ? (metrics.documentation.filesUpToDate / metrics.documentation.filesTotal) * 100
      : 0;
  regions.push({
    id: 'documentation',
    name: 'Documentation',
    position: [0, -2, -1],
    status: getRegionStatus(docProgress, 0),
    progress: docProgress,
    illumination: docProgress / 100,
  });

  return regions;
}

/**
 * Get region status based on progress and failure count
 * NOTE: 1 failure is tolerable (shows in color but not critical)
 * Multiple failures (>1) mark the region as critical for immediate attention
 */
function getRegionStatus(progress: number, failedCount: number): HealthStatus {
  if (progress === 0) return 'offline';

  // Multiple failures (>1) mark region as critical
  if (failedCount > 1) return 'critical';

  // Without failures, use standard thresholds
  if (progress >= 90) return 'optimal';
  if (progress >= 70) return 'healthy';
  if (progress >= 40) return 'warning';
  return 'critical';
}

/**
 * Get color based on health status (for React components)
 */
export function getStatusColor(status: HealthStatus): string {
  switch (status) {
    case 'optimal':
      return '#00ff9f'; // Neon green
    case 'healthy':
      return '#00f0ff'; // Cyan
    case 'warning':
      return '#ffa500'; // Orange
    case 'critical':
      return '#ff0055'; // Red
    case 'offline':
    default:
      return '#1a1f3a'; // Dark
  }
}

/**
 * Format test result message
 */
export function formatTestMessage(passed: number, total: number): string {
  if (total === 0) return 'No tests configured';
  const percentage = Math.round((passed / total) * 100);
  return `${passed}/${total} tests passed (${percentage}%)`;
}

/**
 * Calculate regression percentage
 * @param previous - Previous metrics
 * @param current - Current metrics
 * @returns Regression percentage (negative = improvement, positive = regression)
 */
export function calculateRegression(
  previous: ProjectMetrics,
  current: ProjectMetrics
): number {
  const prevIllumination = calculateIllumination(previous);
  const currIllumination = calculateIllumination(current);

  return ((prevIllumination - currIllumination) / prevIllumination) * 100;
}
