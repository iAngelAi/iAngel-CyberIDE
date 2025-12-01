import { z } from 'zod';

/**
 * Zod Schemas for Backend WebSocket Messages
 *
 * These schemas provide runtime validation for the types defined in
 * src/types/backend.ts. They ensure that data coming from the Python
 * backend matches exactly what the frontend expects.
 */

// --- Shared Enums ---

export const BackendRegionStatusSchema = z.enum(['healthy', 'warning', 'error', 'offline']);
export const BackendDiagnosticLevelSchema = z.enum(['CAUTION', 'ALERT']);

// --- Sub-Schemas ---

export const BackendBrainRegionSchema = z.object({
  status: BackendRegionStatusSchema,
  coverage: z.number().min(0).max(100).optional().default(0), // Handles potential missing fields gracefully
  test_count: z.number().int().nonnegative(),
  passing_tests: z.number().int().nonnegative(),
  failing_tests: z.number().int().nonnegative(),
  file_count: z.number().int().nonnegative(),
  last_modified: z.string().datetime({ offset: true }).nullable(), // Validates ISO 8601
});

export const BackendDiagnosticSchema = z.object({
  level: BackendDiagnosticLevelSchema,
  region: z.string(),
  message: z.string(),
  details: z.string().nullable(),
  timestamp: z.string().datetime({ offset: true }),
  file_path: z.string().nullable(),
  line_number: z.number().int().nullable(),
});

// --- Main Payload Schemas ---

export const BackendNeuralStatusSchema = z.object({
  illumination: z.number().min(0).max(1.0),
  regions: z.record(z.string(), BackendBrainRegionSchema),
  diagnostics: z.array(BackendDiagnosticSchema),
  timestamp: z.string().datetime({ offset: true }),
  project_name: z.string(),
  version: z.string(),
  has_license: z.boolean(),
  has_readme: z.boolean(),
  documentation_complete: z.boolean(),
  api_configured: z.boolean(),
  mcp_providers_count: z.number().int().nonnegative(),
});

export const BackendFileChangeEventSchema = z.object({
  event_type: z.string(), // Could be enum if strict: 'created' | 'modified' | ...
  file_path: z.string(),
  is_test_file: z.boolean(),
  timestamp: z.string().datetime({ offset: true }),
});

export const BackendTestResultSchema = z.object({
  total_tests: z.number().int().nonnegative(),
  passed: z.number().int().nonnegative(),
  failed: z.number().int().nonnegative(),
  skipped: z.number().int().nonnegative(),
  errors: z.number().int().nonnegative(),
  coverage_percentage: z.number().min(0).max(100),
  duration: z.number().nonnegative(),
  timestamp: z.string().datetime({ offset: true }),
  failed_tests: z.array(z.object({
    test_name: z.string().optional(),
    file_path: z.string().optional(),
    error_message: z.string().optional(),
  })),
});

// --- The Root Message Schema ---

/**
 * Validates the entire WebSocket message envelope.
 * Uses discriminated unions to ensure 'data' matches 'type'.
 */
export const BackendWebSocketMessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('neural_status'),
    data: BackendNeuralStatusSchema,
    timestamp: z.string().datetime({ offset: true }),
  }),
  z.object({
    type: z.literal('file_change'),
    data: BackendFileChangeEventSchema,
    timestamp: z.string().datetime({ offset: true }),
  }),
  z.object({
    type: z.literal('test_result'),
    data: BackendTestResultSchema,
    timestamp: z.string().datetime({ offset: true }),
  }),
  z.object({
    type: z.literal('diagnostic'),
    data: BackendDiagnosticSchema,
    timestamp: z.string().datetime({ offset: true }),
  }),
]);

// Infer the type from the schema to ensure it matches your manual types
export type ValidatedWebSocketMessage = z.infer<typeof BackendWebSocketMessageSchema>;
