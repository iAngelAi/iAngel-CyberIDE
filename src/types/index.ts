/**
 * CyberIDE Type Definitions
 * Neural Core - Project Metrics & State Management
 */

// Project health status
export type HealthStatus = 'offline' | 'critical' | 'warning' | 'healthy' | 'optimal';

// Alert severity levels
export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

// Neural region states (for brain visualization)
export interface NeuralRegion {
  id: string;
  name: string;
  position: [number, number, number]; // x, y, z coordinates
  status: HealthStatus;
  progress: number; // 0-100
  illumination: number; // 0-1 (brightness level)
}

// Project metrics that drive the neural visualization
export interface ProjectMetrics {
  // Core modules
  coreModules: {
    total: number;
    completed: number;
    inProgress: number;
    failed: number;
  };

  // Tests
  tests: {
    total: number;
    passed: number;
    failed: number;
    coverage: number; // 0-100
  };

  // Documentation
  documentation: {
    filesTotal: number;
    filesUpToDate: number;
    lastUpdated: Date | null;
  };

  // API/MCP Integrations
  integrations: {
    required: number;
    configured: number;
    validated: number;
  };

  // License & Legal
  license: {
    required: boolean;
    configured: boolean;
    valid: boolean;
  };

  // Overall health
  overallHealth: HealthStatus;
  lastCheck: Date;
}

// Diagnostic alert
export interface DiagnosticAlert {
  id: string;
  severity: AlertSeverity;
  region: string; // Neural region affected
  message: string;
  details: string;
  timestamp: Date;
  resolved: boolean;
}

// Project configuration settings
export interface ProjectSettings {
  projectName: string;
  language: 'javascript' | 'typescript' | 'python' | 'rust' | 'go';
  framework?: string;
  testFramework?: string;

  // Success criteria
  successCriteria: {
    minTestCoverage: number; // 0-100
    requiredModules: string[];
    requiredIntegrations: string[];
    documentationRequired: boolean;
    licenseRequired: boolean;
  };

  // LLM Configuration
  llm: {
    provider: 'anthropic' | 'openai' | 'custom';
    model: string;
    customPrompts?: string[];
    autoGenerate: boolean;
  };

  // Monitoring
  monitoring: {
    enabled: boolean;
    checkInterval: number; // milliseconds
    alertThreshold: number; // 0-100
  };
}

// Brain visualization state
export interface BrainState {
  rotation: [number, number, number]; // x, y, z rotation
  zoomLevel: number;
  autoRotate: boolean;
  regions: NeuralRegion[];
  activeRegion: string | null;
  illuminationLevel: number; // 0-1 (overall brightness)
}

// Project state (Redux/Zustand)
export interface ProjectState {
  settings: ProjectSettings | null;
  metrics: ProjectMetrics;
  alerts: DiagnosticAlert[];
  brain: BrainState;
  isInitialized: boolean;
  isMonitoring: boolean;
}

// Test result
export interface TestResult {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number; // milliseconds
  error?: string;
  region?: string; // Associated neural region
}

// Module definition
export interface Module {
  id: string;
  name: string;
  path: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  tests: TestResult[];
  neuralRegionId: string;
}
