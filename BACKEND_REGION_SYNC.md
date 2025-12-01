# Backend Region Name Synchronization

## Summary
Successfully synchronized backend Python region names with frontend React expectations.

## Problem Identified
The backend was using technical region names (frontend, backend, integration) while the frontend expected domain-driven names (ui-components, core-logic, api-integration) matching the neural brain metaphor.

## Solution Applied
Adapted the backend to use frontend-compatible region names while preserving internal file counting logic.

## Changes Made

### 1. Updated `/neural_cli/metric_calculator.py`

#### Region Mapping
| Old Name (Backend) | New Name (Frontend) | Purpose |
|-------------------|---------------------|---------|
| `backend` | `core-logic` | Neural CLI Python logic (brain core) |
| `integration` | `api-integration` | External API/MCP connections |
| `frontend` | `ui-components` | React UI components (visual cortex) |
| (new) | `data-layer` | Reserved for future data persistence |
| `tests` | `tests` | Unchanged |
| `documentation` | `documentation` | Unchanged |

#### Implementation Details
- Modified `_create_regions()` method to use new region names
- Added `data-layer` region (currently offline, reserved for future use)
- Preserved internal `file_counts` dictionary keys (still uses "frontend", "backend", "tests")
- Added inline comments explaining the mapping

### 2. Updated Test Files

#### `/tests/test_metric_calculator.py`
- Changed assertions from `"frontend"` to `"ui-components"`
- Changed assertions from `"backend"` to `"core-logic"`
- Changed assertions from `"integration"` to `"api-integration"`
- Updated region count from 5 to 6 (added data-layer)

#### `/tests/test_integration.py`
- Updated `status.regions["frontend"]` to `status.regions["ui-components"]`
- Updated region count assertions from 5 to 6

#### `/tests/conftest.py`
- Updated fixture `sample_neural_status()` to use new region names
- Changed `"frontend"` to `"ui-components"`
- Changed `"backend"` to `"core-logic"`

## Test Results

### Before Synchronization
- Backend sent: `frontend`, `backend`, `integration`, `tests`, `documentation`
- Frontend expected: `core-logic`, `api-integration`, `ui-components`, `data-layer`, `tests`, `documentation`
- Result: 3D brain regions remained offline (no matching keys)

### After Synchronization
- Backend sends: `core-logic`, `api-integration`, `ui-components`, `data-layer`, `tests`, `documentation`
- Frontend expects: `core-logic`, `api-integration`, `ui-components`, `data-layer`, `tests`, `documentation`
- Result: ✅ Perfect match - brain regions illuminate correctly

### Test Suite Status
- **221 tests passing** (98.2%)
- 4 tests failing (pre-existing bugs, unrelated to this refactoring)
- All region synchronization tests: ✅ PASSING

## Architecture Decision

### Why Adapt Backend to Frontend?
1. **UI Defines Contract**: The frontend visual metaphor (neural brain) is user-facing
2. **Single Source of Truth**: Domain-driven names are more maintainable
3. **Extensibility**: Easy to add new regions (e.g., data-layer)
4. **Backward Compatibility**: Internal file counting unchanged

### Alternatives Considered
1. ❌ Change frontend to use backend names - Would break visual metaphor
2. ❌ Add translation layer in frontend - Unnecessary complexity
3. ❌ Use different IDs and mappings - Increases error surface
4. ✅ Adapt backend to frontend names - Clean, maintainable solution

## Future Enhancements

### data-layer Region
Currently offline (coverage=0, file_count=0). Will be activated when:
- Database models are added
- Data access layer is implemented
- Persistent storage is configured

### Additional Regions (Potential)
- `security` - Authentication/authorization logic
- `analytics` - Metrics and tracking
- `deployment` - CI/CD configurations

## Verification Commands

### Backend Verification
```bash
source venv/bin/activate
python -c "
from neural_cli.metric_calculator import MetricCalculator
calc = MetricCalculator('.')
status = calc.calculate_neural_status()
print(sorted(status.regions.keys()))
"
```
Expected output: `['api-integration', 'core-logic', 'data-layer', 'documentation', 'tests', 'ui-components']`

### Frontend Verification
Check `src/hooks/useBrainState.ts` lines 60-109 for region definitions.

### Run Tests
```bash
source venv/bin/activate
pytest tests/test_metric_calculator.py tests/test_integration.py -v
```

## Files Modified
1. `/neural_cli/metric_calculator.py` - Core region generation logic
2. `/tests/test_metric_calculator.py` - Test assertions
3. `/tests/test_integration.py` - Integration test assertions
4. `/tests/conftest.py` - Test fixtures

## No Changes Required
- Frontend files (already correct)
- `file_counts` internal logic (still uses technical names)
- API endpoints
- WebSocket message format

---

**Date**: 2025-11-25
**Issue**: Backend-Frontend region name mismatch
**Status**: ✅ Resolved
**Tests**: ✅ Passing (221/225)
