/**
 * Test Suite: Zod Schema Validation
 *
 * PURPOSE: Validate that Zod schemas correctly match Python Pydantic models
 * RULE 1 COMPLIANCE: Ensures mock data passes validation
 *
 * These tests verify the "Triangle of Truth":
 * - TypeScript types (static)
 * - Zod schemas (runtime)
 * - Python Pydantic models (backend)
 */

import { describe, it, expect } from 'vitest';
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
import {
  createMockWebSocketMessage_NeuralStatus,
  createMockWebSocketMessage_FileChange,
  createMockWebSocketMessage_TestResult,
  createMockWebSocketMessage_Diagnostic,
  createMockBrainRegion,
  createMockDiagnostic,
  createMockNeuralStatus,
  createMockFileChangeEvent,
  createMockTestResult,
  invalidMocks,
} from '../helpers/mockData';

describe('Schema Validation: BackendBrainRegion', () => {
  it('should accept valid brain region data', () => {
    const validRegion = createMockBrainRegion();
    const result = BackendBrainRegionSchema.safeParse(validRegion);

    expect(result.success).toBe(true);
  });

  it('should reject coverage out of bounds (negative)', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      coverage: -10, // INVALID
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: new Date().toISOString(),
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('coverage');
    }
  });

  it('should reject coverage out of bounds (>100)', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      coverage: 150, // INVALID
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: new Date().toISOString(),
    });

    expect(result.success).toBe(false);
  });

  it('should reject invalid status enum value', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'invalid_status', // INVALID
      coverage: 50,
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: new Date().toISOString(),
    });

    expect(result.success).toBe(false);
  });

  it('should reject negative test counts', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      coverage: 50,
      test_count: -5, // INVALID
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: new Date().toISOString(),
    });

    expect(result.success).toBe(false);
  });

  it('should reject invalid datetime format', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      coverage: 50,
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: 'not-a-datetime', // INVALID
    });

    expect(result.success).toBe(false);
  });

  it('should accept null last_modified', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      coverage: 50,
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: null, // VALID
    });

    expect(result.success).toBe(true);
  });

  it('should default coverage to 0 if missing', () => {
    const result = BackendBrainRegionSchema.safeParse({
      status: 'healthy',
      // coverage: missing
      test_count: 10,
      passing_tests: 10,
      failing_tests: 0,
      file_count: 5,
      last_modified: null,
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.coverage).toBe(0);
    }
  });
});

describe('Schema Validation: BackendDiagnostic', () => {
  it('should accept valid diagnostic data', () => {
    const validDiagnostic = createMockDiagnostic();
    const result = BackendDiagnosticSchema.safeParse(validDiagnostic);

    expect(result.success).toBe(true);
  });

  it('should reject invalid diagnostic level', () => {
    const result = BackendDiagnosticSchema.safeParse({
      level: 'INVALID', // INVALID
      region: 'test',
      message: 'Test message',
      details: null,
      timestamp: new Date().toISOString(),
      file_path: null,
      line_number: null,
    });

    expect(result.success).toBe(false);
  });

  it('should accept CAUTION level', () => {
    const diagnostic = createMockDiagnostic({ level: 'CAUTION' });
    const result = BackendDiagnosticSchema.safeParse(diagnostic);

    expect(result.success).toBe(true);
  });

  it('should accept ALERT level', () => {
    const diagnostic = createMockDiagnostic({ level: 'ALERT' });
    const result = BackendDiagnosticSchema.safeParse(diagnostic);

    expect(result.success).toBe(true);
  });

  it('should accept null optional fields', () => {
    const diagnostic = createMockDiagnostic({
      details: null,
      file_path: null,
      line_number: null,
    });
    const result = BackendDiagnosticSchema.safeParse(diagnostic);

    expect(result.success).toBe(true);
  });
});

describe('Schema Validation: BackendNeuralStatus', () => {
  it('should accept valid neural status data', () => {
    const validStatus = createMockNeuralStatus();
    const result = BackendNeuralStatusSchema.safeParse(validStatus);

    expect(result.success).toBe(true);
  });

  it('should reject illumination out of bounds (negative)', () => {
    const result = BackendNeuralStatusSchema.safeParse({
      illumination: -0.5, // INVALID
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
    });

    expect(result.success).toBe(false);
  });

  it('should reject illumination out of bounds (>1.0)', () => {
    const result = BackendNeuralStatusSchema.safeParse({
      illumination: 1.5, // INVALID
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
    });

    expect(result.success).toBe(false);
  });

  it('should accept illumination at boundaries (0.0 and 1.0)', () => {
    const result1 = BackendNeuralStatusSchema.safeParse({
      illumination: 0.0,
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
    });

    const result2 = BackendNeuralStatusSchema.safeParse({
      illumination: 1.0,
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
    });

    expect(result1.success).toBe(true);
    expect(result2.success).toBe(true);
  });

  it('should accept empty regions object', () => {
    const status = createMockNeuralStatus({ regions: {} });
    const result = BackendNeuralStatusSchema.safeParse(status);

    expect(result.success).toBe(true);
  });

  it('should accept multiple regions', () => {
    const status = createMockNeuralStatus({
      regions: {
        'region-1': createMockBrainRegion(),
        'region-2': createMockBrainRegion({ status: 'warning' }),
        'region-3': createMockBrainRegion({ status: 'error' }),
      },
    });
    const result = BackendNeuralStatusSchema.safeParse(status);

    expect(result.success).toBe(true);
  });

  it('should accept empty diagnostics array', () => {
    const status = createMockNeuralStatus({ diagnostics: [] });
    const result = BackendNeuralStatusSchema.safeParse(status);

    expect(result.success).toBe(true);
  });

  it('should accept diagnostics with multiple entries', () => {
    const status = createMockNeuralStatus({
      diagnostics: [
        createMockDiagnostic({ level: 'CAUTION' }),
        createMockDiagnostic({ level: 'ALERT', region: 'tests' }),
      ],
    });
    const result = BackendNeuralStatusSchema.safeParse(status);

    expect(result.success).toBe(true);
  });
});

describe('Schema Validation: BackendFileChangeEvent', () => {
  it('should accept valid file change event', () => {
    const validEvent = createMockFileChangeEvent();
    const result = BackendFileChangeEventSchema.safeParse(validEvent);

    expect(result.success).toBe(true);
  });

  it('should accept different event types', () => {
    const events = ['created', 'modified', 'deleted', 'moved'];

    events.forEach((eventType) => {
      const event = createMockFileChangeEvent({ event_type: eventType });
      const result = BackendFileChangeEventSchema.safeParse(event);
      expect(result.success).toBe(true);
    });
  });

  it('should accept test and non-test files', () => {
    const testFile = createMockFileChangeEvent({ is_test_file: true });
    const regularFile = createMockFileChangeEvent({ is_test_file: false });

    expect(BackendFileChangeEventSchema.safeParse(testFile).success).toBe(true);
    expect(BackendFileChangeEventSchema.safeParse(regularFile).success).toBe(true);
  });
});

describe('Schema Validation: BackendTestResult', () => {
  it('should accept valid test result', () => {
    const validResult = createMockTestResult();
    const result = BackendTestResultSchema.safeParse(validResult);

    expect(result.success).toBe(true);
  });

  it('should reject negative test counts', () => {
    const result = BackendTestResultSchema.safeParse({
      total_tests: -5, // INVALID
      passed: 0,
      failed: 0,
      skipped: 0,
      errors: 0,
      coverage_percentage: 0,
      duration: 0,
      timestamp: new Date().toISOString(),
      failed_tests: [],
    });

    expect(result.success).toBe(false);
  });

  it('should reject coverage percentage out of bounds', () => {
    const result = BackendTestResultSchema.safeParse({
      total_tests: 10,
      passed: 10,
      failed: 0,
      skipped: 0,
      errors: 0,
      coverage_percentage: 150, // INVALID
      duration: 1.5,
      timestamp: new Date().toISOString(),
      failed_tests: [],
    });

    expect(result.success).toBe(false);
  });

  it('should accept empty failed_tests array', () => {
    const result = createMockTestResult({ failed_tests: [] });
    const parsed = BackendTestResultSchema.safeParse(result);

    expect(parsed.success).toBe(true);
  });

  it('should accept failed_tests with partial fields', () => {
    const result = createMockTestResult({
      failed_tests: [
        { test_name: 'test1' },
        { file_path: '/test.py' },
        { error_message: 'Error' },
        {},
      ],
    });
    const parsed = BackendTestResultSchema.safeParse(result);

    expect(parsed.success).toBe(true);
  });
});

describe('Schema Validation: BackendWebSocketMessage (Discriminated Union)', () => {
  it('should accept valid neural_status message', () => {
    const message = createMockWebSocketMessage_NeuralStatus();
    const result = BackendWebSocketMessageSchema.safeParse(message);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.type).toBe('neural_status');
    }
  });

  it('should accept valid file_change message', () => {
    const message = createMockWebSocketMessage_FileChange();
    const result = BackendWebSocketMessageSchema.safeParse(message);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.type).toBe('file_change');
    }
  });

  it('should accept valid test_result message', () => {
    const message = createMockWebSocketMessage_TestResult();
    const result = BackendWebSocketMessageSchema.safeParse(message);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.type).toBe('test_result');
    }
  });

  it('should accept valid diagnostic message', () => {
    const message = createMockWebSocketMessage_Diagnostic();
    const result = BackendWebSocketMessageSchema.safeParse(message);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.type).toBe('diagnostic');
    }
  });

  it('should reject message with missing required fields', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.missingRequiredFields);

    expect(result.success).toBe(false);
  });

  it('should reject message with invalid illumination', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.invalidIllumination);

    expect(result.success).toBe(false);
  });

  it('should reject message with invalid coverage', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.invalidCoverage);

    expect(result.success).toBe(false);
  });

  it('should reject message with invalid datetime', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.invalidDatetime);

    expect(result.success).toBe(false);
  });

  it('should reject message with invalid enum value', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.invalidEnumValue);

    expect(result.success).toBe(false);
  });

  it('should reject message with wrong type', () => {
    const result = BackendWebSocketMessageSchema.safeParse(invalidMocks.wrongMessageType);

    expect(result.success).toBe(false);
  });

  it('should reject message with type/data mismatch', () => {
    const result = BackendWebSocketMessageSchema.safeParse({
      type: 'neural_status',
      data: createMockFileChangeEvent(), // MISMATCH: file_change data with neural_status type
      timestamp: new Date().toISOString(),
    });

    expect(result.success).toBe(false);
  });
});

describe('Schema Validation: Edge Cases', () => {
  it('should handle ISO 8601 datetime with timezone', () => {
    const datetimes = [
      new Date().toISOString(), // Standard
      '2024-01-15T10:30:00Z', // UTC
      '2024-01-15T10:30:00+05:00', // Positive offset
      '2024-01-15T10:30:00-08:00', // Negative offset
    ];

    datetimes.forEach((dt) => {
      const region = createMockBrainRegion({ last_modified: dt });
      const result = BackendBrainRegionSchema.safeParse(region);
      expect(result.success).toBe(true);
    });
  });

  it('should handle floating point precision for illumination', () => {
    const values = [0.0, 0.1, 0.5, 0.999999, 1.0];

    values.forEach((val) => {
      const status = createMockNeuralStatus({ illumination: val });
      const result = BackendNeuralStatusSchema.safeParse(status);
      expect(result.success).toBe(true);
    });
  });

  it('should handle special characters in file paths', () => {
    const paths = [
      '/src/utils/helpers.ts',
      'C:\\Users\\Test\\project\\file.py',
      '/path/with spaces/file.ts',
      '/path/with-dashes_and_underscores.ts',
      '/path/with.multiple.dots.ts',
    ];

    paths.forEach((path) => {
      const event = createMockFileChangeEvent({ file_path: path });
      const result = BackendFileChangeEventSchema.safeParse(event);
      expect(result.success).toBe(true);
    });
  });

  it('should handle unicode characters in messages', () => {
    const messages = [
      'Test avec accents: éàâ',
      'Emoji test: 🧪🧠✅',
      'Chinese: 测试',
      'Arabic: اختبار',
    ];

    messages.forEach((msg) => {
      const diagnostic = createMockDiagnostic({ message: msg });
      const result = BackendDiagnosticSchema.safeParse(diagnostic);
      expect(result.success).toBe(true);
    });
  });
});
