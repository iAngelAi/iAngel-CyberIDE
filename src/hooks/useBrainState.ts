import { useState, useCallback, useEffect } from 'react';
import type { BrainState, ProjectMetrics, NeuralRegion, HealthStatus } from '../types';
import type { BackendNeuralStatus, BackendRegionStatus } from '../types/backend';
import { generateNeuralRegions, calculateIllumination } from '../utils/brainHelpers';

/**
 * Map backend region status to frontend health status
 */
function mapBackendStatusToHealthStatus(status: BackendRegionStatus): HealthStatus {
  const statusMap: Record<BackendRegionStatus, HealthStatus> = {
    healthy: 'healthy',
    warning: 'warning',
    error: 'critical',
    offline: 'offline',
  };
  return statusMap[status];
}

/**
 * Calculate illumination level based on coverage and status
 */
function calculateRegionIllumination(coverage: number, status: BackendRegionStatus): number {
  // Base illumination from coverage (0-100 -> 0-1)
  let illumination = coverage / 100;

  // Adjust based on status
  switch (status) {
    case 'healthy':
      illumination = Math.max(illumination, 0.8); // Healthy regions glow even with lower coverage
      break;
    case 'warning':
      illumination *= 0.7; // Slightly dimmed
      break;
    case 'error':
      illumination *= 0.5; // Significantly dimmed, will pulse red
      break;
    case 'offline':
      illumination = 0; // Completely dark
      break;
  }

  return Math.max(0, Math.min(1, illumination));
}

/**
 * Calculate progress percentage from test results
 */
function calculateRegionProgress(passingTests: number, totalTests: number): number {
  if (totalTests === 0) return 0;
  return Math.round((passingTests / totalTests) * 100);
}

/**
 * Custom hook for managing the Neural Brain state
 *
 * Provides methods to update brain visualization based on project metrics
 * and handle user interactions.
 */
export function useBrainState(initialMetrics?: ProjectMetrics) {
  const defaultRegions: NeuralRegion[] = [
    {
      id: 'core-logic',
      name: 'Core Logic',
      position: [2, 1, 0],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
    {
      id: 'api-integration',
      name: 'API Integration',
      position: [1.5, -1, 1.5],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
    {
      id: 'ui-components',
      name: 'UI Components',
      position: [-1.5, 1, 1.5],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
    {
      id: 'data-layer',
      name: 'Data Layer',
      position: [-2, -1, 0],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
    {
      id: 'tests',
      name: 'Tests',
      position: [0, 2, -1],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
    {
      id: 'documentation',
      name: 'Documentation',
      position: [0, -2, -1],
      status: 'offline',
      progress: 0,
      illumination: 0,
    },
  ];

  const [brainState, setBrainState] = useState<BrainState>({
    rotation: [0, 0, 0],
    zoomLevel: 8,
    autoRotate: true,
    regions: defaultRegions,
    activeRegion: null,
    illuminationLevel: 0,
  });

  /**
   * Update brain state based on project metrics
   */
  const updateFromMetrics = useCallback((metrics: ProjectMetrics) => {
    const newRegions = generateNeuralRegions(metrics);
    const illumination = calculateIllumination(metrics);

    setBrainState((prev) => ({
      ...prev,
      regions: newRegions,
      illuminationLevel: illumination,
    }));
  }, []);

  /**
   * Update a specific neural region
   */
  const updateRegion = useCallback((regionId: string, updates: Partial<NeuralRegion>) => {
    setBrainState((prev) => ({
      ...prev,
      regions: prev.regions.map((region) =>
        region.id === regionId ? { ...region, ...updates } : region
      ),
    }));
  }, []);

  /**
   * Set active region (for highlighting/focus)
   */
  const setActiveRegion = useCallback((regionId: string | null) => {
    setBrainState((prev) => ({
      ...prev,
      activeRegion: regionId,
    }));
  }, []);

  /**
   * Toggle auto-rotation
   */
  const toggleAutoRotate = useCallback(() => {
    setBrainState((prev) => ({
      ...prev,
      autoRotate: !prev.autoRotate,
    }));
  }, []);

  /**
   * Set zoom level
   */
  const setZoomLevel = useCallback((zoom: number) => {
    setBrainState((prev) => ({
      ...prev,
      zoomLevel: Math.max(5, Math.min(15, zoom)), // Clamp between 5-15
    }));
  }, []);

  /**
   * Reset brain to offline state
   */
  const reset = useCallback(() => {
    setBrainState((prev) => ({
      ...prev,
      regions: prev.regions.map((region) => ({
        ...region,
        status: 'offline',
        progress: 0,
        illumination: 0,
      })),
      illuminationLevel: 0,
      activeRegion: null,
    }));
  }, []);

  /**
   * Update brain state from backend neural status
   *
   * This is the primary integration point between WebSocket messages
   * and the brain visualization.
   */
  const updateFromBackend = useCallback((backendStatus: BackendNeuralStatus) => {
    setBrainState((prev) => {
      // Map backend regions to frontend regions
      const updatedRegions = prev.regions.map((region) => {
        const backendRegion = backendStatus.regions[region.id];

        // If backend doesn't have this region, keep it as offline
        if (!backendRegion) {
          return {
            ...region,
            status: 'offline' as const,
            progress: 0,
            illumination: 0,
          };
        }

        // Map backend data to frontend format with proper typing
        const status = mapBackendStatusToHealthStatus(backendRegion.status);
        const progress = calculateRegionProgress(
          backendRegion.passing_tests,
          backendRegion.test_count
        );
        const illumination = calculateRegionIllumination(
          backendRegion.coverage,
          backendRegion.status
        );

        return {
          ...region,
          status,
          progress,
          illumination,
        };
      });

      return {
        ...prev,
        regions: updatedRegions,
        illuminationLevel: backendStatus.illumination,
      };
    });
  }, []);

  /**
   * Set error state for a specific region with diagnostic message
   *
   * Used when receiving diagnostic messages from backend.
   */
  const setRegionError = useCallback((regionId: string, message: string) => {
    setBrainState((prev) => ({
      ...prev,
      regions: prev.regions.map((region) =>
        region.id === regionId
          ? {
              ...region,
              status: 'critical' as const,
              illumination: 0.5, // Dimmed red
            }
          : region
      ),
      activeRegion: message, // Show diagnostic message in UI
    }));
  }, []);

  /**
   * Simulate progressive activation (for demo/testing)
   */
  const simulateActivation = useCallback((delayMs: number = 800) => {
    const activateRegion = (index: number) => {
      if (index >= brainState.regions.length) {
        setBrainState((prev) => ({
          ...prev,
          illuminationLevel: 1,
          activeRegion: 'SYSTEM OPTIMAL',
        }));
        return;
      }

      setTimeout(() => {
        setBrainState((prev) => {
          const newRegions = [...prev.regions];
          newRegions[index] = {
            ...newRegions[index],
            status: 'healthy',
            progress: 100,
            illumination: 1,
          };

          return {
            ...prev,
            regions: newRegions,
            activeRegion: newRegions[index].name,
            illuminationLevel: (index + 1) / prev.regions.length,
          };
        });

        activateRegion(index + 1);
      }, delayMs);
    };

    activateRegion(0);
  }, [brainState.regions.length]);

  // Initialize from metrics if provided
  useEffect(() => {
    if (initialMetrics) {
      updateFromMetrics(initialMetrics);
    }
  }, [initialMetrics, updateFromMetrics]);

  return {
    brainState,
    updateFromMetrics,
    updateFromBackend,
    updateRegion,
    setActiveRegion,
    setRegionError,
    toggleAutoRotate,
    setZoomLevel,
    reset,
    simulateActivation,
  };
}
