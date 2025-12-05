# GitHub Copilot Instructions - iAngel Labs

## Project Overview

**iAngel Labs** is a Multi-Agent Development Labs environment focused on building high-quality, compliant, and scalable applications using a sophisticated multi-agent architecture.

**Core Philosophy**: Quality and long-term vision ALWAYS take precedence over short-term speed.

## Stack & Standards

### TypeScript (Node.js 20 LTS)
- **Strict Mode**: Enforce `standards/tsconfig.strict.json` at all times
- **Validation**: Use Zod with `safeParse()` - NEVER use `as` type casting
- **Types**: NEVER use `any` - use `unknown` with type guards instead
- **Database**: Drizzle ORM with PostgreSQL + Row-Level Security (RLS)
- **Testing**: Vitest for unit and integration tests

### Python (3.10-3.12)
- **Strict Mode**: Follow `standards/pyproject.strict.toml` configuration
- **Validation**: Use Pydantic v2 models - NEVER use untyped `dict`
- **Exceptions**: NEVER use generic exceptions - use named exceptions
- **Linting**: Ruff for linting and formatting
- **Type Checking**: mypy in strict mode
- **Logging**: structlog for structured logging

## Legal & Compliance Requirements

**CRITICAL**: All features handling personal data MUST comply with:
- **Loi 25** (Quebec privacy law)
- **PIPEDA** (Canadian federal privacy law)
- **RGPD/GDPR** (if handling EU resident data)

### Privacy by Design Principles
1. **Validation**: All external data MUST be validated at entry points
2. **Security**: Row-Level Security (RLS) is mandatory for user data access
3. **Audit Trail**: All sensitive operations MUST be logged
4. **Consent**: Explicit, informed, granular consent for data collection
5. **PII Protection**: Personal Identifiable Information must be masked in logs

## Multi-Agent Architecture

This repository uses a 13-agent specialized team structure:

### Pillar 1: Strategy, Product & Process
1. **TPM** (Technical Product Manager) - Product vision, roadmap, specifications
2. **Architecte Principal** - System architecture, technical decisions, ADRs
3. **Coach Agile** - Process optimization, team efficiency, ceremonies

### Pillar 2: Application Engineering & UX
4. **Concepteur UX/UI** - User research, design system, WCAG 2.1 AA compliance
5. **Développeur Full-Stack** - Frontend/backend development, API design
6. **Ingénieur Backend MCP** - High-performance systems (Go/Rust/C++)
7. **Ingénieur Graphique 3D** - 3D applications (Unity/Unreal/WebGL)

### Pillar 3: Data & AI
8. **Ingénieur de Données** - ETL/ELT pipelines, data quality, governance
9. **Scientifique des Données** - ML/AI models, research, bias detection
10. **Ingénieur MLOps** - Model deployment, monitoring, drift detection

### Pillar 4: Infrastructure & Compliance (DevSecOps)
11. **Ingénieur DevOps/SRE** - Infrastructure as Code, CI/CD, observability
12. **Ingénieur QA Automation** - Test strategy, automated testing, quality metrics
13. **Spécialiste Sécurité Conformité** - Security audits, compliance validation

## Code Quality Standards

### Absolute Rules
1. **NO "quick fixes"** - Always identify and fix root causes
2. **Zero linting errors** - Code must pass all linters
3. **Zero type errors** - Strict typing must be maintained
4. **Test coverage > 80%** - All code must be thoroughly tested
5. **No flaky tests** - Tests must be deterministic and stable

### API Design
- **REST**: Use kebab-case URLs, camelCase JSON
- **GraphQL**: Schema-first approach with typed resolvers
- **Documentation**: OpenAPI/Swagger required
- **Versioning**: Use /v1/, /v2/ for API versions
- **Pagination**: Required for all list endpoints

### Security Best Practices (OWASP Top 10)
1. **Access Control**: Implement proper authorization checks
2. **Cryptography**: Use appropriate encryption for sensitive data
3. **Injection Prevention**: Validate and sanitize all inputs
4. **Secure Design**: Security by design, not as an afterthought
5. **Security Configuration**: Secure default configurations
6. **Dependency Management**: Keep dependencies updated and scanned
7. **Authentication**: Robust authentication and session management
8. **Integrity**: Verify software and data integrity
9. **Logging**: Comprehensive security logging and monitoring
10. **SSRF Prevention**: Validate all server-side requests

### Testing Pyramid
- **70% Unit Tests**: Fast, focused, isolated tests
- **20% Integration Tests**: API, database, service integration
- **10% E2E Tests**: Critical user journeys (Playwright/Cypress)

## Architecture Patterns

### Preferred Patterns
- **Hexagonal Architecture**: Isolate domain from infrastructure
- **Event Sourcing**: Native audit trail for compliance
- **CQRS**: When read/write patterns diverge
- **Circuit Breaker**: For resilience in distributed systems

### Documentation
- **ADR Required**: All significant architectural decisions must be documented as Architecture Decision Records (ADR)
- **Format**: Context, Decision, Consequences, Alternatives Considered

## Development Workflow

### Before Writing Code
1. Read relevant standard files (`standards/tsconfig.strict.json` or `standards/pyproject.strict.toml`)
2. Understand the User Story and acceptance criteria
3. Identify technical dependencies
4. Check for existing patterns in the codebase

### When Writing Code
1. Write clean, typed, documented code
2. Use atomic commits with conventional commit messages
3. Create clear PR descriptions
4. Ensure all tests pass
5. Validate linting and type checking

### Before Merging
1. Zero linting errors
2. Zero type errors
3. All tests passing
4. Code coverage > 80%
5. Security scan passed
6. Code review approved

## Performance Requirements

### Backend Services
- **Latency**: p99 < 500ms for API endpoints
- **Throughput**: Design for 10x current load
- **Availability**: 99.9% uptime minimum
- **Monitoring**: Prometheus metrics + distributed tracing

### Frontend/3D Applications
- **Framerate**: 60 FPS minimum (90 FPS for VR)
- **Load Time**: < 3 seconds for initial load
- **Bundle Size**: Optimize and code-split
- **Accessibility**: WCAG 2.1 AA compliance mandatory

## When Generating Code

### TypeScript Example (with Zod validation)
```typescript
import { z } from "zod";

// Define schema
const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  age: z.number().int().positive().optional(),
});

// Infer type
type User = z.infer<typeof UserSchema>;

// Safe parsing
function createUser(input: unknown): User {
  const result = UserSchema.safeParse(input);
  if (!result.success) {
    throw new ValidationError(result.error.format());
  }
  return result.data; // Properly typed
}
```

### Python Example (with Pydantic)
```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    age: int | None = Field(default=None, gt=0)

def create_user(input_data: dict) -> User:
    # Automatic validation by Pydantic
    user = User(**input_data)
    return user
```

## Logging Best Practices

Always use structured logging and mask PII:

```python
import structlog

logger = structlog.get_logger()

# Good - Structured with masked PII
logger.info(
    "user_action",
    user_id=user_id,
    action="profile_update",
    fields=["name", "preferences"]  # Don't log actual values
)

# Bad - Unstructured with PII
logger.info(f"User {email} updated profile with data {data}")
```

## Infrastructure as Code

- **All infrastructure MUST be managed as code** (Terraform/Pulumi)
- **NO manual changes** in production
- **State management**: Version controlled and locked
- **Change process**: PR → Review → Merge → Apply

## Accessibility

All UI components must meet **WCAG 2.1 AA** standards:
- Color contrast ratio ≥ 4.5:1 (text), ≥ 3:1 (large text)
- Full keyboard navigation support
- ARIA labels for screen readers
- No information conveyed by color alone
- Content readable at 200% zoom

## Anti-Patterns to Avoid

### Never Do This
- ❌ Type casting with `as` in TypeScript
- ❌ Using `any` type
- ❌ Generic exceptions in Python
- ❌ Untyped dictionaries
- ❌ Manual database operations without RLS
- ❌ Logging PII without masking
- ❌ Skipping tests for "quick fixes"
- ❌ Manual infrastructure changes
- ❌ Non-deterministic tests
- ❌ Features without compliance validation

## Key Reminders for Copilot

1. **Quality > Speed**: Take time to do it right
2. **Type Safety**: Strict typing is non-negotiable
3. **Validation**: All external data must be validated
4. **Security**: Consider OWASP Top 10 in every feature
5. **Privacy**: Loi 25/PIPEDA compliance for all data handling
6. **Testing**: Comprehensive test coverage required
7. **Documentation**: ADRs for architectural decisions
8. **Accessibility**: WCAG 2.1 AA compliance mandatory
9. **Performance**: Design for scale and resilience
10. **Observability**: Metrics, logs, and traces for all services

## Questions or Clarifications?

When in doubt about:
- **Product decisions** → Refer to TPM agent specifications
- **Architecture** → Refer to Architecte Principal guidelines
- **Security/Compliance** → Refer to Spécialiste Sécurité Conformité
- **Standards** → Check `standards/tsconfig.strict.json` or `standards/pyproject.strict.toml`

---

**Remember**: This is a long-term project where quality, security, and compliance are paramount. Every line of code should reflect professional excellence and adherence to these standards.
