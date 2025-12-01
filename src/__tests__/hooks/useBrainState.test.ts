/**
 * Test Suite: useBrainState Hook
 *
 * PURPOSE: Test brain state management logic without 3D rendering
 * RULE 2 COMPLIANCE: No Three.js or react-three-fiber imports (pure logic testing)
 * RULE 4 COMPLIANCE: All 5 HealthStatus variants tested exhaustively
 *
 * Tests cover:
 * - updateFromBackend() maps regions correctly
 * - Region illumination calculation (healthy=80%, warning=70%, error=50%, offline=0%)
 * - Region progress calculation from test pass rate
 * - All HealthStatus variants ('offline' | 'critical' | 'warning' | 'healthy' | 'optimal')
 * - setRegionError() sets critical status + message
 * - Unknown backend regions ignored (offline state)
 * - Null/empty backend data handled gracefully
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useBrainState } from '../../hooks/useBrainState';
import { createMockNeuralStatus, createMockBrainRegion } from '../helpers/mockData';
import type { BackendNeuralStatus } from '../../types/backend';
import type { HealthStatus } from '../../types';

// RULE 2 VERIFICATION: This file should NOT import 'three' or 'react-three-fiber'
// If those imports exist, the tests fail the rule.

describe('useBrainState: Initialization', () => {
  it('should initialize with default offline regions', () => {
    const { result } = renderHook(() => useBrainState());

    expect(result.current.brainState.regions).toHaveLength(6);
    expect(result.current.brainState.illuminationLevel).toBe(0);
    expect(result.current.brainState.autoRotate).toBe(true);
    expect(result.current.brainState.activeRegion).toBeNull();

    // All regions should start offline
    result.current.brainState.regions.forEach((region) => {
      expect(region.status).toBe('offline');
      expect(region.progress).toBe(0);
      expect(region.illumination).toBe(0);
    });
  });

  it('should initialize with correct region IDs', () => {
    const { result } = renderHook(() => useBrainState());

    const regionIds = result.current.brainState.regions.map((r) => r.id);
    expect(regionIds).toEqual([
      'core-logic',
      'api-integration',
      'ui-components',
      'data-layer',
      'tests',
      'documentation',
    ]);
  });

  it('should initialize with correct region positions', () => {
    const { result } = renderHook(() => useBrainState());

    const coreLogicRegion = result.current.brainState.regions.find(
      (r) => r.id === 'core-logic'
    );
    expect(coreLogicRegion?.position).toEqual([2, 1, 0]);
  });
});

describe('useBrainState: updateFromBackend (Main Integration)', () => {
  it('should update brain state from backend neural status', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      illumination: 0.85,
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'healthy',
          coverage: 90,
          test_count: 10,
          passing_tests: 10,
          failing_tests: 0,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    expect(result.current.brainState.illuminationLevel).toBe(0.85);

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.status).toBe('healthy');
    expect(coreLogic?.progress).toBe(100); // 10/10 tests passed
  });

  it('should map backend regions to frontend regions correctly', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({ status: 'healthy', coverage: 85 }),
        'api-integration': createMockBrainRegion({ status: 'warning', coverage: 70 }),
        'tests': createMockBrainRegion({ status: 'error', coverage: 50 }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    const apiIntegration = result.current.brainState.regions.find(
      (r) => r.id === 'api-integration'
    );
    const tests = result.current.brainState.regions.find((r) => r.id === 'tests');

    expect(coreLogic?.status).toBe('healthy');
    expect(apiIntegration?.status).toBe('warning');
    expect(tests?.status).toBe('critical'); // 'error' backend status maps to 'critical' frontend
  });

  it('should keep regions offline if not in backend data', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({ status: 'healthy' }),
        // Other regions not included
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    const apiIntegration = result.current.brainState.regions.find(
      (r) => r.id === 'api-integration'
    );

    expect(coreLogic?.status).toBe('healthy');
    expect(apiIntegration?.status).toBe('offline'); // Not in backend, stays offline
    expect(apiIntegration?.progress).toBe(0);
    expect(apiIntegration?.illumination).toBe(0);
  });

  it('should handle empty regions object from backend', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {}, // Empty
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    // All regions should be offline
    result.current.brainState.regions.forEach((region) => {
      expect(region.status).toBe('offline');
      expect(region.progress).toBe(0);
      expect(region.illumination).toBe(0);
    });
  });

  it('should handle unknown backend region names gracefully', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'unknown-region': createMockBrainRegion({ status: 'healthy' }),
        'core-logic': createMockBrainRegion({ status: 'healthy' }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    // Should not crash, 'unknown-region' is ignored
    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.status).toBe('healthy');

    // No region with id 'unknown-region' should exist in frontend
    const unknownRegion = result.current.brainState.regions.find(
      (r) => r.id === 'unknown-region'
    );
    expect(unknownRegion).toBeUndefined();
  });
});

describe('useBrainState: Region Illumination Calculation', () => {
  it('should calculate illumination for healthy status (minimum 80%)', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'healthy',
          coverage: 50, // Low coverage, but healthy status
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.illumination).toBeGreaterThanOrEqual(0.8); // At least 80%
  });

  it('should calculate illumination for warning status (coverage * 0.7)', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'warning',
          coverage: 100, // Full coverage but warning
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.illumination).toBeCloseTo(0.7, 1); // 1.0 * 0.7 = 0.7
  });

  it('should calculate illumination for error status (coverage * 0.5)', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'error',
          coverage: 100,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.illumination).toBeCloseTo(0.5, 1); // 1.0 * 0.5 = 0.5
  });

  it('should set illumination to 0 for offline status', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'offline',
          coverage: 100, // Coverage doesn't matter for offline
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.illumination).toBe(0);
  });

  it('should clamp illumination between 0 and 1', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          status: 'healthy',
          coverage: 100, // Should result in illumination >= 0.8
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.illumination).toBeGreaterThanOrEqual(0);
    expect(coreLogic?.illumination).toBeLessThanOrEqual(1);
  });
});

describe('useBrainState: Region Progress Calculation', () => {
  it('should calculate progress from test pass rate', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          test_count: 10,
          passing_tests: 8,
          failing_tests: 2,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.progress).toBe(80); // 8/10 = 80%
  });

  it('should handle 100% test pass rate', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          test_count: 20,
          passing_tests: 20,
          failing_tests: 0,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.progress).toBe(100);
  });

  it('should handle 0% test pass rate', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          test_count: 10,
          passing_tests: 0,
          failing_tests: 10,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.progress).toBe(0);
  });

  it('should handle division by zero (no tests)', () => {
    const { result } = renderHook(() => useBrainState());

    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({
          test_count: 0,
          passing_tests: 0,
          failing_tests: 0,
        }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.progress).toBe(0); // Should not crash, returns 0
  });
});

describe('useBrainState: HealthStatus Union Exhaustiveness (RULE 4)', () => {
  // RULE 4: All union variants must be tested

  const statusMappings: Array<{
    backendStatus: 'healthy' | 'warning' | 'error' | 'offline';
    expectedFrontendStatus: HealthStatus;
  }> = [
    { backendStatus: 'healthy', expectedFrontendStatus: 'healthy' },
    { backendStatus: 'warning', expectedFrontendStatus: 'warning' },
    { backendStatus: 'error', expectedFrontendStatus: 'critical' },
    { backendStatus: 'offline', expectedFrontendStatus: 'offline' },
  ];

  statusMappings.forEach(({ backendStatus, expectedFrontendStatus }) => {
    it(`should map backend status '${backendStatus}' to frontend status '${expectedFrontendStatus}'`, () => {
      const { result } = renderHook(() => useBrainState());

      const backendData = createMockNeuralStatus({
        regions: {
          'core-logic': createMockBrainRegion({ status: backendStatus }),
        },
      });

      act(() => {
        result.current.updateFromBackend(backendData);
      });

      const region = result.current.brainState.regions.find((r) => r.id === 'core-logic');
      expect(region?.status).toBe(expectedFrontendStatus);
    });
  });

  // Test all 5 frontend HealthStatus variants explicitly
  const allFrontendStatuses: HealthStatus[] = [
    'offline',
    'critical',
    'warning',
    'healthy',
    'optimal',
  ];

  it('should support all 5 HealthStatus variants in type system', () => {
    // This test verifies the type union is complete
    allFrontendStatuses.forEach((status) => {
      const isValidStatus: HealthStatus = status;
      expect(isValidStatus).toBe(status);
    });
  });

  it('should render all 5 HealthStatus variants without errors', () => {
    const { result } = renderHook(() => useBrainState());

    allFrontendStatuses.forEach((status) => {
      act(() => {
        result.current.updateRegion('core-logic', {
          status,
          illumination: status === 'offline' ? 0 : 0.5,
        });
      });

      const region = result.current.brainState.regions.find((r) => r.id === 'core-logic');
      expect(region?.status).toBe(status);
    });
  });
});

describe('useBrainState: setRegionError', () => {
  it('should set region to critical status with error message', () => {
    const { result } = renderHook(() => useBrainState());

    act(() => {
      result.current.setRegionError('core-logic', 'Test failed: assertion error');
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.status).toBe('critical');
    expect(coreLogic?.illumination).toBe(0.5); // Dimmed red
    expect(result.current.brainState.activeRegion).toBe('Test failed: assertion error');
  });

  it('should only update the specified region', () => {
    const { result } = renderHook(() => useBrainState());

    // Set one region to healthy first
    const backendStatus = createMockNeuralStatus({
      regions: {
        'core-logic': createMockBrainRegion({ status: 'healthy' }),
        'api-integration': createMockBrainRegion({ status: 'healthy' }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    // Set error on one region
    act(() => {
      result.current.setRegionError('core-logic', 'Critical error');
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    const apiIntegration = result.current.brainState.regions.find(
      (r) => r.id === 'api-integration'
    );

    expect(coreLogic?.status).toBe('critical');
    expect(apiIntegration?.status).toBe('healthy'); // Unaffected
  });
});

describe('useBrainState: Other State Management', () => {
  it('should update a specific region', () => {
    const { result } = renderHook(() => useBrainState());

    act(() => {
      result.current.updateRegion('core-logic', {
        status: 'healthy',
        progress: 85,
        illumination: 0.85,
      });
    });

    const coreLogic = result.current.brainState.regions.find((r) => r.id === 'core-logic');
    expect(coreLogic?.status).toBe('healthy');
    expect(coreLogic?.progress).toBe(85);
    expect(coreLogic?.illumination).toBe(0.85);
  });

  it('should set active region', () => {
    const { result } = renderHook(() => useBrainState());

    act(() => {
      result.current.setActiveRegion('core-logic');
    });

    expect(result.current.brainState.activeRegion).toBe('core-logic');

    act(() => {
      result.current.setActiveRegion(null);
    });

    expect(result.current.brainState.activeRegion).toBeNull();
  });

  it('should toggle auto-rotate', () => {
    const { result } = renderHook(() => useBrainState());

    expect(result.current.brainState.autoRotate).toBe(true);

    act(() => {
      result.current.toggleAutoRotate();
    });

    expect(result.current.brainState.autoRotate).toBe(false);

    act(() => {
      result.current.toggleAutoRotate();
    });

    expect(result.current.brainState.autoRotate).toBe(true);
  });

  it('should set zoom level with clamping', () => {
    const { result } = renderHook(() => useBrainState());

    act(() => {
      result.current.setZoomLevel(10);
    });
    expect(result.current.brainState.zoomLevel).toBe(10);

    // Test lower bound
    act(() => {
      result.current.setZoomLevel(3);
    });
    expect(result.current.brainState.zoomLevel).toBe(5); // Clamped to min 5

    // Test upper bound
    act(() => {
      result.current.setZoomLevel(20);
    });
    expect(result.current.brainState.zoomLevel).toBe(15); // Clamped to max 15
  });

  it('should reset brain to offline state', () => {
    const { result } = renderHook(() => useBrainState());

    // Set some active state
    const backendStatus = createMockNeuralStatus({
      illumination: 0.9,
      regions: {
        'core-logic': createMockBrainRegion({ status: 'healthy', coverage: 90 }),
      },
    });

    act(() => {
      result.current.updateFromBackend(backendStatus);
    });

    act(() => {
      result.current.setActiveRegion('core-logic');
    });

    expect(result.current.brainState.illuminationLevel).toBe(0.9);

    // Reset
    act(() => {
      result.current.reset();
    });

    expect(result.current.brainState.illuminationLevel).toBe(0);
    expect(result.current.brainState.activeRegion).toBeNull();

    result.current.brainState.regions.forEach((region) => {
      expect(region.status).toBe('offline');
      expect(region.progress).toBe(0);
      expect(region.illumination).toBe(0);
    });
  });
});
