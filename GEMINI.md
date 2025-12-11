# GEMINI.md — CyberIDE Configuration

Version: 2.1.0
Project: CyberIDE — Neural IDE with 3D Visualization
Type: Personal Project (no Loi 25/PIPEDA constraints)
Last Updated: 2025-12-11

---

## Hierarchy and Scope

This file configures Gemini CLI behavior for this project only.
Settings in `.gemini/settings.json` define MCP server configurations.
For shared project information (architecture, commands), see `CLAUDE.md` or `README.md`.

IMPORTANT: Gemini CLI does not support @import directives. All rules are inline.

---

## MCP Server Tiers

This project uses a 4-tier MCP activation strategy to optimize context window usage.
Configuration source: `.gemini/settings.json`

### TIER 1: Always Active (3 tools)

These servers load automatically on every session.

| Server | Tools | Purpose |
|--------|-------|---------|
| context7 | 2 | Library documentation (Three.js, React, FastAPI, Pydantic) |
| sequentialthinking | 1 | Structured reasoning, anti-reward-hacking |

Usage: No activation required.

```
Query: "Explain useFrame from R3F"
Response: context7 provides up-to-date docs automatically
```

### TIER 2: On-Demand Development (29 tools)

Activate explicitly with @mention when needed.

| Server | Tools | Purpose | Activation |
|--------|-------|---------|------------|
| github-official | 20 | PR, Issues, Code Review | @github |
| ast-grep | 1 | AST-based code search | @ast-grep |
| semgrep | 8 | SAST/SCA security scanning | @semgrep |

Denied tools (security):
- delete_file (GitHub)
- merge_pull_request (requires human review)

Confirmation required:
- create_pull_request
- push_files

```
Query: "@github create PR for feature/brain-optimization"
Query: "@semgrep scan for security issues in neural_cli/"
```

### TIER 3: CI/Testing (32 tools)

For E2E testing and browser automation. High timeout tolerance required.

| Server | Tools | Purpose | Activation |
|--------|-------|---------|------------|
| playwright-mcp-server | 32 | E2E tests, screenshots | @playwright |

Denied tools (security):
- playwright_upload_file (exfiltration risk)

```
Query: "@playwright generate E2E tests for Brain3D component"
Query: "@playwright screenshot http://localhost:5173 --full-page"
```

### TIER 4: Sandboxed Execution (1 tool)

Isolated Python REPL with no network access.

| Server | Tools | Purpose | Activation |
|--------|-------|---------|------------|
| mcp-code-interpreter | 1 | Python REPL, data analysis | @interpreter |

Sandbox restrictions:
- network: disabled
- allowed directories: /workspace, /tmp only

```
Query: "@interpreter analyze test coverage trends from pytest output"
```

---

## Token Budgets

Configured limits to prevent context overflow:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| tool_output_token_budget | 4,096 | Max tokens per tool response |
| model_context_window | 100,000 | Target context size |
| model_max_output_tokens | 8,192 | Max generation length |
| tool_budget_ratio | 4% | tool_budget / context_window |

Rule: Do not activate all tiers simultaneously. Deactivate after use.

---

## Timeouts

Server-specific timeouts based on operation complexity:

| Server | Startup | Execution | Notes |
|--------|---------|-----------|-------|
| context7 | 15s | 30s | Fast docs lookup |
| sequentialthinking | 10s | 60s | Extended reasoning |
| github-official | 20s | 45s | API rate limits |
| ast-grep | 10s | 30s | Fast AST parsing |
| semgrep | 30s | 120s | Deep scanning |
| playwright-mcp-server | 60s | 180s | Browser operations |
| mcp-code-interpreter | 20s | 60s | Code execution |

---

## Tech Stack Reference

Frontend: React 19, Three.js/R3F, Tailwind CSS, Vitest
Backend: Python 3.10+, FastAPI, Pydantic V2, pytest
Build: Vite, TypeScript strict

Ports:
- 5173: Vite dev server (frontend)
- 8000: FastAPI (backend + WebSocket)

---

## TypeScript Standards (Inline)

Priority: CRITICAL
Scope: All .ts, .tsx files


### Forbidden Patterns

```typescript
// FORBIDDEN: Type casting
const data = response as UserData;
const element = event.target as HTMLInputElement;

// FORBIDDEN: any type
function process(data: any): any { ... }
let config: any = {};

// FORBIDDEN: Non-null assertion
const element = document.getElementById('app')!;
const value = obj.prop!.nested!.value;
```

### Required Patterns

```typescript
// REQUIRED: Zod validation at boundaries
import { z } from 'zod';

const NeuralStatusSchema = z.object({
  illumination: z.number().min(0).max(100),
  regions: z.array(BrainRegionSchema),
  lastUpdate: z.string().datetime(),
  errorState: z.union([ErrorInfoSchema, z.null()]),
});

type NeuralStatus = z.infer<typeof NeuralStatusSchema>;

function processStatus(input: unknown): NeuralStatus {
  const result = NeuralStatusSchema.safeParse(input);
  if (!result.success) {
    throw new ValidationError(result.error.format());
  }
  return result.data;
}

// REQUIRED: Type guards for narrowing
function isNeuralStatus(value: unknown): value is NeuralStatus {
  return NeuralStatusSchema.safeParse(value).success;
}

// REQUIRED: Null checks instead of assertions
function getElement(id: string): HTMLElement {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Element ${id} not found`);
  }
  return element;
}
```

---

## Python Standards (Inline)

Priority: CRITICAL
Scope: All .py files

### Forbidden Patterns

```python
# FORBIDDEN: typing.Any
from typing import Any
def process(data: Any) -> Any: ...

# FORBIDDEN: Untyped dict
def get_user() -> dict: ...

# FORBIDDEN: Bare except
try:
    risky_operation()
except:
    pass

# FORBIDDEN: type: ignore without justification
result = func()  # type: ignore
```

### Required Patterns

```python
# REQUIRED: Pydantic V2 models
from pydantic import BaseModel, Field, ConfigDict

class BrainRegion(BaseModel):
    model_config = ConfigDict(strict=True)
    
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    illumination: float = Field(..., ge=0, le=100)
    connections: list[str] = Field(default_factory=list)

class NeuralStatus(BaseModel):
    model_config = ConfigDict(strict=True)
    
    illumination: float = Field(..., ge=0, le=100)
    regions: list[BrainRegion]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    error_state: ErrorInfo | None = None

# REQUIRED: Validation with model_validate
from pydantic import ValidationError

def process_status(data: dict[str, object]) -> NeuralStatus:
    try:
        return NeuralStatus.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid status data: {e}")

# REQUIRED: Specific exception handling
def process_data(data: InputData) -> Result:
    try:
        return risky_operation(data)
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except NetworkError as e:
        logger.warning(f"Network issue: {e}")
        return retry_operation(data)
```

---

## Anti-Reward-Hacking Protocol (Inline)

Priority: ABSOLUTE
Trigger: Any test failure

### Definition

Reward hacking occurs when the AI:
- Modifies a test to make it pass instead of fixing the code
- Removes failing assertions
- Adds skip markers without justification
- Uses catch-all exceptions to mask errors

This is the worst form of technical debt because it hides real problems.

### Forbidden Behaviors

```python
# FORBIDDEN: Modifying test to match bug
def test_calculate_sum():
    # Original: assert calculate_sum(2, 2) == 4
    assert calculate_sum(2, 2) == 5  # Modified to match buggy output

# FORBIDDEN: Removing assertions
def test_user_validation():
    user = create_user(invalid_data)
    # assert user.is_valid == False  # Removed because it failed

# FORBIDDEN: Skip without issue tracker
@pytest.mark.skip("Fails, fix later")
def test_critical_feature(): ...

# FORBIDDEN: Catch-all to hide errors
try:
    return risky_operation(data)
except:
    return None
```


### Required Protocol on Test Failure

Step 1: STOP
Do not modify any test immediately upon failure.

Step 2: DIAGNOSE
```
DIAGNOSTIC REPORT

1. Read the test:
   - Assertion: calculate_sum(2, 2) == 4
   - Expected behavior: 2 + 2 = 4 (correct)

2. Read the source code:
   - File: src/calculator.py
   - Function: calculate_sum(a, b) -> a + b + 1
   - Actual behavior: 2 + 2 + 1 = 5 (incorrect)

3. Verdict: CODE contains bug, TEST is correct
```

Step 3: REQUEST APPROVAL
Before modifying any test logic, request explicit approval.
Provide: problem identified, proposed correction, impact assessment.

Step 4: CORRECT (after approval)
Fix the source code, not the test.

Step 5: VERIFY
```
CORRECTION APPLIED

Result:
- tests/test_calculator.py::test_add PASSED
- No tests modified
- Source code corrected

Neural pathways restored. System optimal.
```

### Checklist Before Any Test Modification

- [ ] Read the complete test
- [ ] Understand what the test verifies
- [ ] Identify if problem is in CODE or TEST
- [ ] If test is incorrect: provide technical justification
- [ ] Request approval before modifying test
- [ ] No skip without linked issue tracker
- [ ] No assertion removal
- [ ] No generic try/except

### Warning Signals

If you find yourself thinking:
- "This test is too strict, I'll soften it" -> STOP
- "I'll skip this for now" -> STOP
- "The assertion isn't really necessary" -> STOP
- "I'll just catch the exception to make it pass" -> STOP

These thoughts indicate reward hacking. Return to diagnosis.

---

## Performance Standards (Three.js/R3F)

Target: 60 FPS constant

### Required Techniques

```typescript
// Level of Detail for distant objects
import { LOD } from 'three';
const lod = new LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(mediumDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);

// Instanced rendering for repeated geometries
import { InstancedMesh } from 'three';
const instancedMesh = new InstancedMesh(geometry, material, count);

// useFrame optimization pattern
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

export function AnimatedBrain() {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5;
    }
  });
  
  return <mesh ref={meshRef}>...</mesh>;
}
```

### Profiling Tools

- Chrome DevTools Performance tab
- Three.js Stats panel
- React DevTools Profiler

---

## Dependency Management (uv)

**Package Manager**: uv v0.9+
**Lockfile**: `uv.lock` (MUST be committed)

### CRITICAL: pip is FORBIDDEN

```bash
# FORBIDDEN - Does not update lockfile
pip install <package>
pip3 install <package>
python -m pip install <package>

# REQUIRED - Updates lockfile automatically
uv add <package>
uv add --dev <package>
```

### Standard Commands

| Action | Command |
|--------|---------|
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Sync from lockfile | `uv sync` |
| CI/CD (frozen) | `uv sync --frozen` |
| Run script | `uv run python script.py` |
| Run tests | `uv run pytest` |
| Update lockfile | `uv lock` |

### Why uv?

1. **Lockfile Authority**: `uv.lock` guarantees reproducible builds
2. **Performance**: 10-100x faster than pip (Rust-based)
3. **Determinism**: Same dependencies across dev/CI/prod

### Migration from pip

If you encounter a project without `uv.lock`:

```bash
uv lock          # Generate lockfile from pyproject.toml
uv sync          # Install dependencies
git add uv.lock  # Commit the lockfile
```

---

## Shell Policies

### Allowed Commands

npm, npx, uv, python, python3, pytest, vitest, git, docker, docker-compose

### Denied Commands

rm -rf, sudo, chmod 777, curl | bash, wget | sh, pip install, pip3 install

### Confirmation Required

git push, npm publish, docker push

---

## Recommended Workflows

### Standard Development (TIER 1 only)

```
"Explain useBrainState hook"
-> context7 provides React/R3F docs
-> sequentialthinking structures response
```

### Code Review (TIER 1 + 2)

```
"@github @semgrep review PR #42 for security issues"
-> github fetches PR diff
-> semgrep scans for vulnerabilities
```

### E2E Testing (TIER 1 + 3)

```
"@playwright generate E2E tests for Brain3D interactions"
-> playwright creates test scenarios
-> context7 provides R3F testing patterns
```

### Data Analysis (TIER 1 + 4)

```
"@interpreter analyze pytest coverage trends"
-> interpreter runs Python analysis in sandbox
```

---

## Coexistence with CLAUDE.md

This project supports both Gemini CLI and Claude Code.

Separation of concerns:
- CLAUDE.md: Claude-specific features (agents, orchestration, hierarchy)
- GEMINI.md: Gemini-specific features (MCP tiers, settings.json)
- README.md: Shared project documentation

Shared information (architecture, commands) appears in CLAUDE.md as the primary source.
GEMINI.md references it rather than duplicating to maintain DRY principle.

In case of conflict between files, the model-specific file takes precedence for that model.

---

## File References

| File | Purpose |
|------|---------|
| .gemini/settings.json | MCP server configuration |
| .gemini/standards/*.md | Archived standards (integrated inline above) |
| CLAUDE.md | Claude Code configuration |
| README.md | Project documentation |

---

## Version History

- 2.1.0 (2025-12-11): Add uv package manager, forbid pip install, update shell policies
- 2.0.0 (2025-12-11): Lab AI Senior compliance, inline standards, MCP tiers
- 1.0.0 (2025-12-01): Initial version

---

CyberIDE — Neural Architect — Lab AI Senior Configuration
