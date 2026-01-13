# MetricsMonitor Component

## Overview

The MetricsMonitor component provides real-time visualization of Neural Core performance metrics. It displays key performance indicators (KPIs) in a cyberpunk-themed interface that aligns with the CyberIDE design language.

## Features

- **Real-time Monitoring**: Polls metrics every 5 seconds (configurable)
- **3 KPI Cards**:
  - **Neural Load**: Transactions per second (TPS)
  - **Cognitive Latency**: Average operation latency in milliseconds
  - **System Health**: Overall health status with color-coded indicators
- **Cyberpunk/Neon Styling**: Consistent with CyberIDE design system
- **Health Status Indicators**:
  - Healthy (Green): Error rate < 5%, Latency < 500ms
  - Degraded (Amber): Error rate 5-10%, Latency 500-1000ms
  - Critical (Red): Error rate > 10%, Latency > 1000ms

## Architecture

### Backend API

**Endpoint**: `GET /api/metrics/summary`

**Response Format**:
```json
{
  "transactions_per_second": 125.5,
  "average_latency_ms": 94.48,
  "error_rate": 6.25,
  "health_status": "degraded",
  "timestamp": "2025-12-16T15:01:17.000000+00:00",
  "total_operations": 48
}
```

**Implementation Details**:
- Reads the last 5 metrics files from the `./metrics` directory
- Aggregates metrics across all operations
- Calculates TPS based on time range of operations
- Determines health status based on error rate and latency thresholds

### Frontend Component

**Location**: `src/components/MetricsMonitor/MetricsMonitor.tsx`

**Props**:
```typescript
interface MetricsMonitorProps {
  pollIntervalMs?: number; // Default: 5000 (5 seconds)
}
```

**State Management**:
- Uses React `useState` for metrics data
- Uses `useEffect` with polling interval for data fetching
- Handles loading, error, and success states

## Integration

The MetricsMonitor component is integrated into the GitDashboard as a new tab:

```tsx
import { MetricsMonitor } from '../MetricsMonitor';

// In GitDashboard component
{activeTab === 'metrics' && (
  <MetricsMonitor pollIntervalMs={5000} />
)}
```

## Usage

### Basic Usage

```tsx
import { MetricsMonitor } from '@/components/MetricsMonitor';

function MyComponent() {
  return <MetricsMonitor />;
}
```

### Custom Poll Interval

```tsx
<MetricsMonitor pollIntervalMs={10000} /> // Poll every 10 seconds
```

## Styling

The component uses TailwindCSS with custom cyber-themed classes:

- `bg-cyber-darker`: Dark background for cards
- `border-cyber-primary`: Neon border colors
- `text-cyber-primary`: Cyan primary text
- Gradient hover effects for neon glow
- Pulsing animations for status indicators

## Testing

### Generate Sample Metrics

```bash
python3 test_metrics_api.py
```

This script:
1. Creates a MetricsManager instance
2. Generates 48 sample operations (API requests, DB queries, computations, errors)
3. Writes metrics to the `./metrics` directory
4. Validates the API endpoint calculation logic

### Validate Backend Logic

```bash
python3 test_backend_endpoint.py
```

This script:
1. Reads metrics files from `./metrics`
2. Calculates summary statistics
3. Validates all required fields are present
4. Displays the calculated results

## Performance Considerations

- **Polling**: Uses `setInterval` with configurable interval
- **Memory**: Minimal state (only current metrics snapshot)
- **Network**: Lightweight JSON payload (~200 bytes)
- **Rendering**: Efficient React updates on metric changes

## Security

- No PII in metrics (enforced by backend validation)
- CORS configured for localhost development
- Metrics files contain only operational data
- No authentication required (internal monitoring)

## Future Enhancements

- WebSocket support for real-time updates (eliminate polling)
- Historical charts (time-series visualization)
- Configurable alert thresholds
- Export metrics to CSV/JSON
- Metrics filtering by operation type
- Performance budget indicators

## Dependencies

- **React**: ^19.2.0
- **lucide-react**: ^0.554.0 (icons)
- **TailwindCSS**: Styling framework
- **FastAPI**: Backend framework
- **backend.cto.metrics**: Metrics collection system

## References

- [MetricsManager Documentation](../../backend/cto/metrics/README.md)
- [GitDashboard Component](../../src/components/GitDashboard/GitDashboard.tsx)
- [Backend API Routes](../../neural_cli/main.py)
