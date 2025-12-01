/**
 * Test Helper: Zod-Validated Mock Data Factory
 *
 * RULE 1 COMPLIANCE: All mock data MUST pass Zod validation
 * These helpers ensure that test data conforms to runtime schemas.
 */

import {
  BackendWebSocketMessageSchema,
  BackendNeuralStatusSchema,
  BackendBrainRegionSchema,
  BackendFileChangeEventSchema,
  BackendTestResultSchema,
  BackendDiagnosticSchema,
  BackendRegionStatusSchema,
  BackendDiagnosticLevelSchema,
} from '../../schemas/websocketValidation';
import type {
  BackendWebSocketMessage,
  BackendNeuralStatus,
  BackendBrainRegion,
  BackendFileChangeEvent,
  BackendTestResult,
  BackendDiagnostic,
  BackendRegionStatus,
  BackendDiagnosticLevel,
} from '../../types/backend';

/**
 * Validates mock data against Zod schema and throws if invalid
 * This enforces Rule 1 at development time
 */
function validateOrThrow<T>(schema: any, data: T, context: string): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errors = result.error.format();
    throw new Error(
      `[Rule 1 Violation] Mock data failed Zod validation in ${context}:\n${JSON.stringify(errors, null, 2)}`
    );
  }
  return result.data as T;
}

/**
 * Create a mock BrainRegion with validation
 */
export function createMockBrainRegion(
  overrides: Partial<BackendBrainRegion> = {}
): BackendBrainRegion {
  const mock: BackendBrainRegion = {
    status: 'healthy' as BackendRegionStatus,
    coverage: 85,
    test_count: 10,
    passing_tests: 10,
    failing_tests: 0,
    file_count: 15,
    last_modified: new Date().toISOString(),
    ...overrides,
  };

  return validateOrThrow(BackendBrainRegionSchema, mock, 'createMockBrainRegion');
}

/**
 * Create a mock Diagnostic message with validation
 */
export function createMockDiagnostic(
  overrides: Partial<BackendDiagnostic> = {}
): BackendDiagnostic {
  const mock: BackendDiagnostic = {
    level: 'CAUTION' as BackendDiagnosticLevel,
    region: 'core-logic',
    message: 'Test coverage below threshold',
    details: 'Current coverage: 75%. Target: 80%.',
    timestamp: new Date().toISOString(),
    file_path: '/src/utils/helpers.ts',
    line_number: 42,
    ...overrides,
  };

  return validateOrThrow(BackendDiagnosticSchema, mock, 'createMockDiagnostic');
}

/**
 * Create a mock NeuralStatus with validation
 */
export function createMockNeuralStatus(
  overrides: Partial<BackendNeuralStatus> = {}
): BackendNeuralStatus {
  const mock: BackendNeuralStatus = {
    illumination: 0.75,
    regions: {
      'core-logic': createMockBrainRegion({
        status: 'healthy',
        coverage: 85,
        test_count: 10,
        passing_tests: 10,
        failing_tests: 0,
      }),
      'api-integration': createMockBrainRegion({
        status: 'warning',
        coverage: 70,
        test_count: 5,
        passing_tests: 4,
        failing_tests: 1,
      }),
      'tests': createMockBrainRegion({
        status: 'healthy',
        coverage: 90,
        test_count: 20,
        passing_tests: 20,
        failing_tests: 0,
      }),
    },
    diagnostics: [],
    timestamp: new Date().toISOString(),
    project_name: 'CyberIDE',
    version: '1.0.0',
    has_license: true,
    has_readme: true,
    documentation_complete: false,
    api_configured: true,
    mcp_providers_count: 0,
    ...overrides,
  };

  return validateOrThrow(BackendNeuralStatusSchema, mock, 'createMockNeuralStatus');
}

/**
 * Create a mock FileChangeEvent with validation
 */
export function createMockFileChangeEvent(
  overrides: Partial<BackendFileChangeEvent> = {}
): BackendFileChangeEvent {
  const mock: BackendFileChangeEvent = {
    event_type: 'modified',
    file_path: '/src/utils/helpers.ts',
    is_test_file: false,
    timestamp: new Date().toISOString(),
    ...overrides,
  };

  return validateOrThrow(BackendFileChangeEventSchema, mock, 'createMockFileChangeEvent');
}

/**
 * Create a mock TestResult with validation
 */
export function createMockTestResult(
  overrides: Partial<BackendTestResult> = {}
): BackendTestResult {
  const mock: BackendTestResult = {
    total_tests: 10,
    passed: 8,
    failed: 2,
    skipped: 0,
    errors: 0,
    coverage_percentage: 75.5,
    duration: 2.345,
    timestamp: new Date().toISOString(),
    failed_tests: [
      {
        test_name: 'should handle edge case',
        file_path: 'tests/test_edge_cases.py',
        error_message: 'AssertionError: Expected 5 but got 4',
      },
    ],
    ...overrides,
  };

  return validateOrThrow(BackendTestResultSchema, mock, 'createMockTestResult');
}

/**
 * Create a complete WebSocket message (neural_status type)
 */
export function createMockWebSocketMessage_NeuralStatus(
  dataOverrides: Partial<BackendNeuralStatus> = {}
): BackendWebSocketMessage {
  const message = {
    type: 'neural_status' as const,
    data: createMockNeuralStatus(dataOverrides),
    timestamp: new Date().toISOString(),
  };

  return validateOrThrow(
    BackendWebSocketMessageSchema,
    message,
    'createMockWebSocketMessage_NeuralStatus'
  );
}

/**
 * Create a complete WebSocket message (file_change type)
 */
export function createMockWebSocketMessage_FileChange(
  dataOverrides: Partial<BackendFileChangeEvent> = {}
): BackendWebSocketMessage {
  const message = {
    type: 'file_change' as const,
    data: createMockFileChangeEvent(dataOverrides),
    timestamp: new Date().toISOString(),
  };

  return validateOrThrow(
    BackendWebSocketMessageSchema,
    message,
    'createMockWebSocketMessage_FileChange'
  );
}

/**
 * Create a complete WebSocket message (test_result type)
 */
export function createMockWebSocketMessage_TestResult(
  dataOverrides: Partial<BackendTestResult> = {}
): BackendWebSocketMessage {
  const message = {
    type: 'test_result' as const,
    data: createMockTestResult(dataOverrides),
    timestamp: new Date().toISOString(),
  };

  return validateOrThrow(
    BackendWebSocketMessageSchema,
    message,
    'createMockWebSocketMessage_TestResult'
  );
}

/**
 * Create a complete WebSocket message (diagnostic type)
 */
export function createMockWebSocketMessage_Diagnostic(
  dataOverrides: Partial<BackendDiagnostic> = {}
): BackendWebSocketMessage {
  const message = {
    type: 'diagnostic' as const,
    data: createMockDiagnostic(dataOverrides),
    timestamp: new Date().toISOString(),
  };

  return validateOrThrow(
    BackendWebSocketMessageSchema,
    message,
    'createMockWebSocketMessage_Diagnostic'
  );
}

/**
 * Create an INVALID mock for testing validation failures
 * These intentionally violate the schema for negative testing
 */
export const invalidMocks = {
  /**
   * Missing required fields
   */
  missingRequiredFields: {
    type: 'neural_status',
    // Missing 'data' and 'timestamp'
  },

  /**
   * Invalid illumination (out of bounds)
   */
  invalidIllumination: {
    type: 'neural_status',
    data: {
      illumination: 1.5, // INVALID: Must be 0-1
      regions: {},
      diagnostics: [],
      timestamp: new Date().toISOString(),
      project_name: 'Test',
      version: '1.0.0',
      has_license: false,
      has_readme: false,
      documentation_complete: false,
      api_configured: false,
      mcp_providers_count: 0,
    },
    timestamp: new Date().toISOString(),
  },

  /**
   * Invalid coverage (out of bounds)
   */
  invalidCoverage: {
    type: 'neural_status',
    data: {
      illumination: 0.5,
      regions: {
        'test-region': {
          status: 'healthy',
          coverage: 150, // INVALID: Must be 0-100
          test_count: 10,
          passing_tests: 10,
          failing_tests: 0,
          file_count: 5,
          last_modified: new Date().toISOString(),
        },
      },
      diagnostics: [],
      timestamp: new Date().toISOString(),
      project_name: 'Test',
      version: '1.0.0',
      has_license: false,
      has_readme: false,
      documentation_complete: false,
      api_configured: false,
      mcp_providers_count: 0,
    },
    timestamp: new Date().toISOString(),
  },

  /**
   * Invalid datetime format
   */
  invalidDatetime: {
    type: 'neural_status',
    data: {
      illumination: 0.5,
      regions: {},
      diagnostics: [],
      timestamp: 'not-a-valid-datetime', // INVALID: Must be ISO 8601
      project_name: 'Test',
      version: '1.0.0',
      has_license: false,
      has_readme: false,
      documentation_complete: false,
      api_configured: false,
      mcp_providers_count: 0,
    },
    timestamp: new Date().toISOString(),
  },

  /**
   * Invalid enum value
   */
  invalidEnumValue: {
    type: 'diagnostic',
    data: {
      level: 'INVALID_LEVEL', // INVALID: Must be 'CAUTION' | 'ALERT'
      region: 'test',
      message: 'Test',
      details: null,
      timestamp: new Date().toISOString(),
      file_path: null,
      line_number: null,
    },
    timestamp: new Date().toISOString(),
  },

  /**
   * Wrong type for discriminated union
   */
  wrongMessageType: {
    type: 'invalid_type', // INVALID: Not in union
    data: {},
    timestamp: new Date().toISOString(),
  },
};
