/**
 * Test Suite: brainHelpers Utilities
 *
 * PURPOSE: Test pure utility functions for neural brain calculations
 * RULE 2 COMPLIANCE: No Three.js imports - pure logic testing only
 *
 * Tests cover:
 * - calculateIllumination() weighted scoring
 * - generateNeuralRegions() creates regions from metrics
 * - Edge cases: 0% coverage, 100% coverage, division by zero
 * - getStatusColor() mapping
 * - formatTestMessage() formatting
 * - calculateRegression() comparison logic
 */

import { describe, it, expect } from 'vitest';
import {
  calculateIllumination,
  determineHealthStatus,
  generateNeuralRegions,
  getStatusColor,
  formatTestMessage,
  calculateRegression,
} from '../../utils/brainHelpers';
import type { ProjectMetrics, HealthStatus } from '../../types';

// RULE 2 VERIFICATION: This file should NOT import 'three' or 'react-three-fiber'

/**
 * Helper to create mock ProjectMetrics
 */
function createMockProjectMetrics(overrides: Partial<ProjectMetrics> = {}): ProjectMetrics {
  return {
    coreModules: {
      total: 10,
      completed: 8,
      inProgress: 1,
      failed: 1,
    },
    tests: {
      total: 100,
      passed: 85,
      failed: 15,
      coverage: 75,
    },
    documentation: {
      filesTotal: 20,
      filesUpToDate: 15,
      lastUpdated: new Date(),
    },
    integrations: {
      required: 5,
      configured: 4,
      validated: 3,
    },
    license: {
      required: true,
      configured: true,
      valid: true,
    },
    overallHealth: 'healthy',
    lastCheck: new Date(),
    ...overrides,
  };
}

describe('calculateIllumination: Weighted Scoring', () => {
  it('should calculate illumination with proper weights', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 }, // 100% = 0.3
      coreModules: { total: 10, completed: 10, inProgress: 0, failed: 0 }, // 100% = 0.25
      documentation: { filesTotal: 20, filesUpToDate: 20, lastUpdated: new Date() }, // 100% = 0.15
      integrations: { required: 5, configured: 5, validated: 5 }, // 100% = 0.2
      license: { required: true, configured: true, valid: true }, // 100% = 0.1
    });

    const illumination = calculateIllumination(metrics);

    // Total: 0.3 + 0.25 + 0.15 + 0.2 + 0.1 = 1.0
    expect(illumination).toBeCloseTo(1.0, 2);
  });

  it('should handle zero test coverage', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 0, passed: 0, failed: 0, coverage: 0 },
    });

    const illumination = calculateIllumination(metrics);

    // Should not crash, returns partial illumination
    expect(illumination).toBeGreaterThanOrEqual(0);
    expect(illumination).toBeLessThan(1.0);
  });

  it('should handle zero modules', () => {
    const metrics = createMockProjectMetrics({
      coreModules: { total: 0, completed: 0, inProgress: 0, failed: 0 },
    });

    const illumination = calculateIllumination(metrics);

    expect(illumination).toBeGreaterThanOrEqual(0);
    expect(illumination).toBeLessThanOrEqual(1.0);
  });

  it('should handle division by zero in all categories', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 0, passed: 0, failed: 0, coverage: 0 },
      coreModules: { total: 0, completed: 0, inProgress: 0, failed: 0 },
      documentation: { filesTotal: 0, filesUpToDate: 0, lastUpdated: null },
      integrations: { required: 0, configured: 0, validated: 0 },
    });

    const illumination = calculateIllumination(metrics);

    // Should handle gracefully, not crash
    expect(illumination).toBeGreaterThanOrEqual(0);
    expect(illumination).toBeLessThanOrEqual(1.0);
    expect(Number.isNaN(illumination)).toBe(false);
  });

  it('should calculate partial illumination correctly', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 50, failed: 50, coverage: 50 }, // 50% = 0.15
      coreModules: { total: 10, completed: 5, inProgress: 2, failed: 3 }, // 50% = 0.125
      documentation: { filesTotal: 20, filesUpToDate: 10, lastUpdated: new Date() }, // 50% = 0.075
      integrations: { required: 4, configured: 2, validated: 2 }, // 50% = 0.1
      license: { required: true, configured: true, valid: true }, // 100% = 0.1
    });

    const illumination = calculateIllumination(metrics);

    // Total: 0.15 + 0.125 + 0.075 + 0.1 + 0.1 = 0.55
    expect(illumination).toBeCloseTo(0.55, 2);
  });

  it('should clamp illumination between 0 and 1', () => {
    // Test lower bound
    const lowMetrics = createMockProjectMetrics({
      tests: { total: 100, passed: 0, failed: 100, coverage: 0 },
      coreModules: { total: 10, completed: 0, inProgress: 0, failed: 10 },
      documentation: { filesTotal: 20, filesUpToDate: 0, lastUpdated: null },
      integrations: { required: 5, configured: 0, validated: 0 },
      license: { required: true, configured: false, valid: false },
    });

    const lowIllumination = calculateIllumination(lowMetrics);
    expect(lowIllumination).toBeGreaterThanOrEqual(0);

    // Test upper bound
    const highMetrics = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 },
      coreModules: { total: 10, completed: 10, inProgress: 0, failed: 0 },
      documentation: { filesTotal: 20, filesUpToDate: 20, lastUpdated: new Date() },
      integrations: { required: 5, configured: 5, validated: 5 },
      license: { required: true, configured: true, valid: true },
    });

    const highIllumination = calculateIllumination(highMetrics);
    expect(highIllumination).toBeLessThanOrEqual(1.0);
  });

  it('should handle no integrations required (considers complete)', () => {
    const metrics = createMockProjectMetrics({
      integrations: { required: 0, configured: 0, validated: 0 },
    });

    const illumination = calculateIllumination(metrics);

    // With no integrations required, contribution should be 0.2 (full weight)
    expect(illumination).toBeGreaterThan(0);
  });

  it('should handle license not required (considers complete)', () => {
    const metrics = createMockProjectMetrics({
      license: { required: false, configured: false, valid: false },
    });

    const illumination = calculateIllumination(metrics);

    // With no license required, contribution should be 0.1 (full weight)
    expect(illumination).toBeGreaterThan(0);
  });
});

describe('determineHealthStatus: Status Determination', () => {
  it('should return "optimal" for high illumination (>= 90%)', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 },
      coreModules: { total: 10, completed: 10, inProgress: 0, failed: 0 },
      documentation: { filesTotal: 20, filesUpToDate: 20, lastUpdated: new Date() }, // 100% docs
      integrations: { required: 5, configured: 5, validated: 5 }, // 100% integrations
      license: { required: true, configured: true, valid: true },
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('optimal');
  });

  it('should return "healthy" for good illumination (>= 70%)', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 85, failed: 15, coverage: 75 },
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('healthy');
  });

  it('should return "warning" for moderate illumination (>= 40%)', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 75, failed: 25, coverage: 50 }, // 25% failure (< 30% threshold)
      coreModules: { total: 10, completed: 5, inProgress: 3, failed: 2 }, // 50% progress
      documentation: { filesTotal: 20, filesUpToDate: 10, lastUpdated: new Date() }, // 50% docs
      integrations: { required: 5, configured: 3, validated: 2 }, // 40% integrations
      license: { required: true, configured: true, valid: true },
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('warning');
  });

  it('should return "critical" for low illumination (> 0%)', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 10, failed: 90, coverage: 10 },
      coreModules: { total: 10, completed: 1, inProgress: 0, failed: 9 },
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('critical');
  });

  it('should return "offline" for zero illumination', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 0, passed: 0, failed: 0, coverage: 0 },
      coreModules: { total: 0, completed: 0, inProgress: 0, failed: 0 },
      documentation: { filesTotal: 0, filesUpToDate: 0, lastUpdated: null },
      integrations: { required: 5, configured: 0, validated: 0 }, // Required but none configured
      license: { required: true, configured: false, valid: false }, // Required but invalid
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('offline');
  });

  it('should return "critical" if core modules have failures', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 },
      coreModules: { total: 10, completed: 8, inProgress: 0, failed: 2 }, // Has failures
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('critical');
  });

  it('should return "critical" if >30% tests failing', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 60, failed: 40, coverage: 60 }, // 40% failing
      coreModules: { total: 10, completed: 10, inProgress: 0, failed: 0 },
    });

    const status = determineHealthStatus(metrics);
    expect(status).toBe('critical');
  });
});

describe('generateNeuralRegions: Region Generation', () => {
  it('should generate regions from project metrics', () => {
    const metrics = createMockProjectMetrics();
    const regions = generateNeuralRegions(metrics);

    expect(regions).toHaveLength(4); // core-logic, api-integration, tests, documentation
    expect(regions.map((r) => r.id)).toEqual([
      'core-logic',
      'api-integration',
      'tests',
      'documentation',
    ]);
  });

  it('should calculate core-logic region correctly', () => {
    const metrics = createMockProjectMetrics({
      coreModules: { total: 10, completed: 8, inProgress: 1, failed: 1 },
    });

    const regions = generateNeuralRegions(metrics);
    const coreLogic = regions.find((r) => r.id === 'core-logic');

    expect(coreLogic?.progress).toBe(80); // 8/10 = 80%
    expect(coreLogic?.status).toBe('healthy');
  });

  it('should calculate api-integration region correctly', () => {
    const metrics = createMockProjectMetrics({
      integrations: { required: 5, configured: 5, validated: 5 },
    });

    const regions = generateNeuralRegions(metrics);
    const apiIntegration = regions.find((r) => r.id === 'api-integration');

    expect(apiIntegration?.progress).toBe(100); // 5/5 = 100%
    expect(apiIntegration?.status).toBe('optimal');
  });

  it('should calculate tests region correctly', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 100, passed: 75, failed: 25, coverage: 75 },
    });

    const regions = generateNeuralRegions(metrics);
    const testsRegion = regions.find((r) => r.id === 'tests');

    expect(testsRegion?.progress).toBe(75);
    expect(testsRegion?.status).toBe('healthy');
  });

  it('should calculate documentation region correctly', () => {
    const metrics = createMockProjectMetrics({
      documentation: { filesTotal: 20, filesUpToDate: 10, lastUpdated: new Date() },
    });

    const regions = generateNeuralRegions(metrics);
    const docsRegion = regions.find((r) => r.id === 'documentation');

    expect(docsRegion?.progress).toBe(50); // 10/20 = 50%
    expect(docsRegion?.status).toBe('warning');
  });

  it('should handle region with failures as critical', () => {
    const metrics = createMockProjectMetrics({
      coreModules: { total: 10, completed: 8, inProgress: 0, failed: 2 },
    });

    const regions = generateNeuralRegions(metrics);
    const coreLogic = regions.find((r) => r.id === 'core-logic');

    expect(coreLogic?.status).toBe('critical');
  });

  it('should handle region with 0 progress as offline', () => {
    const metrics = createMockProjectMetrics({
      tests: { total: 0, passed: 0, failed: 0, coverage: 0 },
    });

    const regions = generateNeuralRegions(metrics);
    const testsRegion = regions.find((r) => r.id === 'tests');

    expect(testsRegion?.status).toBe('offline');
    expect(testsRegion?.progress).toBe(0);
  });

  it('should handle integrations not required as 100% complete', () => {
    const metrics = createMockProjectMetrics({
      integrations: { required: 0, configured: 0, validated: 0 },
    });

    const regions = generateNeuralRegions(metrics);
    const apiIntegration = regions.find((r) => r.id === 'api-integration');

    expect(apiIntegration?.progress).toBe(100);
    expect(apiIntegration?.status).toBe('optimal');
  });
});

describe('getStatusColor: Color Mapping', () => {
  it('should return correct color for optimal status', () => {
    expect(getStatusColor('optimal')).toBe('#00ff9f');
  });

  it('should return correct color for healthy status', () => {
    expect(getStatusColor('healthy')).toBe('#00f0ff');
  });

  it('should return correct color for warning status', () => {
    expect(getStatusColor('warning')).toBe('#ffa500');
  });

  it('should return correct color for critical status', () => {
    expect(getStatusColor('critical')).toBe('#ff0055');
  });

  it('should return correct color for offline status', () => {
    expect(getStatusColor('offline')).toBe('#1a1f3a');
  });

  it('should handle invalid status gracefully', () => {
    expect(getStatusColor('invalid' as any)).toBe('#1a1f3a'); // Default to offline
  });
});

describe('formatTestMessage: Message Formatting', () => {
  it('should format test results with percentage', () => {
    const message = formatTestMessage(85, 100);
    expect(message).toBe('85/100 tests passed (85%)');
  });

  it('should format 100% pass rate', () => {
    const message = formatTestMessage(10, 10);
    expect(message).toBe('10/10 tests passed (100%)');
  });

  it('should format 0% pass rate', () => {
    const message = formatTestMessage(0, 10);
    expect(message).toBe('0/10 tests passed (0%)');
  });

  it('should handle no tests configured', () => {
    const message = formatTestMessage(0, 0);
    expect(message).toBe('No tests configured');
  });

  it('should round percentage correctly', () => {
    const message = formatTestMessage(17, 23); // 73.913...%
    expect(message).toContain('(74%)');
  });
});

describe('calculateRegression: Regression Calculation', () => {
  it('should calculate positive regression (performance decrease)', () => {
    const previous = createMockProjectMetrics({
      tests: { total: 100, passed: 90, failed: 10, coverage: 90 },
    });

    const current = createMockProjectMetrics({
      tests: { total: 100, passed: 70, failed: 30, coverage: 70 },
    });

    const regression = calculateRegression(previous, current);

    expect(regression).toBeGreaterThan(0); // Positive = regression
  });

  it('should calculate negative regression (performance increase)', () => {
    const previous = createMockProjectMetrics({
      tests: { total: 100, passed: 70, failed: 30, coverage: 70 },
    });

    const current = createMockProjectMetrics({
      tests: { total: 100, passed: 90, failed: 10, coverage: 90 },
    });

    const regression = calculateRegression(previous, current);

    expect(regression).toBeLessThan(0); // Negative = improvement
  });

  it('should return 0 for no change', () => {
    const metrics = createMockProjectMetrics();
    const regression = calculateRegression(metrics, metrics);

    expect(regression).toBeCloseTo(0, 1);
  });

  it('should handle division by zero in previous metrics', () => {
    const previous = createMockProjectMetrics({
      tests: { total: 0, passed: 0, failed: 0, coverage: 0 },
      coreModules: { total: 0, completed: 0, inProgress: 0, failed: 0 },
    });

    const current = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 },
    });

    const regression = calculateRegression(previous, current);

    // Should handle gracefully, not crash
    expect(Number.isNaN(regression)).toBe(false);
  });

  it('should calculate large regression correctly', () => {
    const previous = createMockProjectMetrics({
      tests: { total: 100, passed: 100, failed: 0, coverage: 100 },
      coreModules: { total: 10, completed: 10, inProgress: 0, failed: 0 },
    });

    const current = createMockProjectMetrics({
      tests: { total: 100, passed: 10, failed: 90, coverage: 10 },
      coreModules: { total: 10, completed: 1, inProgress: 0, failed: 9 },
    });

    const regression = calculateRegression(previous, current);

    expect(regression).toBeGreaterThan(50); // Significant regression
  });
});
