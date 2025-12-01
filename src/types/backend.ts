/**
 * Backend Type Mappings - Python Pydantic Models → TypeScript
 *
 * These types mirror the Python models in neural_cli/models.py
 * to ensure type safety across the WebSocket boundary.
 */

// Region status (maps to Python RegionStatus enum)
export type BackendRegionStatus = 'healthy' | 'warning' | 'error' | 'offline';

// Diagnostic level (maps to Python DiagnosticLevel enum)
export type BackendDiagnosticLevel = 'CAUTION' | 'ALERT';

// Brain region from backend
export interface BackendBrainRegion {
  status: BackendRegionStatus;
  coverage: number;
  test_count: number;
  passing_tests: number;
  failing_tests: number;
  file_count: number;
  last_modified: string | null; // ISO 8601 datetime
}

// Diagnostic message
export interface BackendDiagnostic {
  level: BackendDiagnosticLevel;
  region: string;
  message: string;
  details: string | null;
  timestamp: string; // ISO 8601 datetime
  file_path: string | null;
  line_number: number | null;
}

// Complete neural status from backend
export interface BackendNeuralStatus {
  illumination: number; // 0.0 - 1.0
  regions: Record<string, BackendBrainRegion>;
  diagnostics: BackendDiagnostic[];
  timestamp: string; // ISO 8601 datetime
  project_name: string;
  version: string;
  has_license: boolean;
  has_readme: boolean;
  documentation_complete: boolean;
  api_configured: boolean;
  mcp_providers_count: number;
}

// File change event
export interface BackendFileChangeEvent {
  event_type: string; // 'created' | 'modified' | 'deleted' | 'moved'
  file_path: string;
  is_test_file: boolean;
  timestamp: string; // ISO 8601 datetime
}

// Test result
export interface BackendTestResult {
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  errors: number;
  coverage_percentage: number;
  duration: number;
  timestamp: string; // ISO 8601 datetime
  failed_tests: Array<{
    test_name?: string;
    file_path?: string;
    error_message?: string;
  }>;
}

// File mapping data from backend
export interface BackendFileMappingData {
  source_files: Array<{
    id: string;
    path: string;
    name: string;
    extension: string;
    linesOfCode: number;
    hasTests: boolean;
    testStatus: string;
  }>;
  test_files: Array<{
    id: string;
    path: string;
    name: string;
    passed: number;
    failed: number;
    skipped: number;
    coverage: number;
    lastRun: string;
  }>;
  connections: Array<{
    id: string;
    source_id: string;
    test_id: string;
    strength: number;
    status: string;
  }>;
}

// Git pulse data
export interface BackendGitPulseData {
  hash: string;
  author: string;
  message: string;
  timestamp: string;
  files_changed: string[];
  intensity: number;
}

// WebSocket message envelope
export interface BackendWebSocketMessage {
  type: 'neural_status' | 'file_change' | 'test_result' | 'diagnostic' | 'file_mapping' | 'git_pulse';
  data: BackendNeuralStatus | BackendFileChangeEvent | BackendTestResult | BackendDiagnostic | BackendFileMappingData | BackendGitPulseData;
  timestamp: string; // ISO 8601 datetime
}

// Type guards for discriminating message types
export function isNeuralStatusMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendNeuralStatus } {
  return msg.type === 'neural_status';
}

export function isFileChangeMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendFileChangeEvent } {
  return msg.type === 'file_change';
}

export function isTestResultMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendTestResult } {
  return msg.type === 'test_result';
}

export function isDiagnosticMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendDiagnostic } {
  return msg.type === 'diagnostic';
}

export function isFileMappingMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendFileMappingData } {
  return msg.type === 'file_mapping';
}

export function isGitPulseMessage(msg: BackendWebSocketMessage): msg is BackendWebSocketMessage & { data: BackendGitPulseData } {
  return msg.type === 'git_pulse';
}
