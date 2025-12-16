# CyberIDE Documentation

## Overview

This directory contains comprehensive documentation for the CyberIDE project - a Neural IDE with 3D brain visualization that reflects project health in real-time.

## Quick Navigation

### Getting Started
- [Quick Start Guide](../QUICKSTART.md) - Get up and running in minutes
- [Installation Guide](guides/installation.md) - Detailed installation instructions
- [Development Guide](guides/development.md) - Set up your development environment

### Architecture
- [Architecture Decision Records](adr/) - Key architectural decisions
  - [ADR-001: Logging Strategy](adr/ADR-001-logging-strategy.md)
  - [ADR-002: Documentation Standards](adr/ADR-002-documentation-standards.md)
- [System Architecture](../README.md#architecture) - High-level system design

### Security & Compliance
- [Security Policy](../SECURITY.md) - Security policies and incident response
- [Security Guides](security/) - Detailed security documentation
  - [DevSecOps CI/CD Guide](security/devsecops_ci_cd_guide.md)
  - [Secrets Management](security/secrets_management_guide.md)
  - [Incident Response](security/incident_response_guide.md)
  - [AI Security](security/ai_security_guide.md)
- [Compliance Checklist](../COMPLIANCE_CHECKLIST.md) - Loi 25, PIPEDA, RGPD compliance

### Development
- [Development Workflow](guides/development.md) - Day-to-day development practices
- [Testing Guide](guides/testing.md) - Writing and running tests
- [Contributing Guidelines](guides/contributing.md) - How to contribute to the project
- [Documentation Guardian](guides/documentation-guardian-workflow.md) - Automated documentation quality checks

### Reports & Metrics
- [Test Reports](reports/) - Test execution reports and metrics
- [Performance Metrics](reports/performance.md) - System performance data

### Reference
- [API Documentation](api/) - API endpoints and WebSocket messages
- [Configuration](guides/configuration.md) - Environment variables and settings
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions

### Archive
- [Archived Documentation](archive/INDEX.md) - Historical documentation

## Documentation Standards

All documentation in this project follows the standards defined in [ADR-002: Documentation Standards](adr/ADR-002-documentation-standards.md).

Key principles:
- Professional formatting without emojis in technical docs
- Relative paths for portability
- Consistent language usage (English for technical, French for user-facing)
- Clear structure and navigation
- Single source of truth for each topic

## Contributing to Documentation

When adding or updating documentation:

1. Follow the standards in ADR-002
2. Update this index if adding new top-level documents
3. Use relative links for cross-references
4. Include code examples where appropriate
5. Test all commands and code snippets
6. Run markdown linter before committing

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── adr/                         # Architecture Decision Records
├── guides/                      # User and developer guides
│   ├── installation.md
│   ├── development.md
│   ├── testing.md
│   ├── configuration.md
│   ├── troubleshooting.md
│   └── contributing.md
├── api/                         # API documentation
├── reports/                     # Test and metrics reports
├── security/                    # Security documentation
│   ├── README.md
│   ├── devsecops_ci_cd_guide.md
│   ├── secrets_management_guide.md
│   ├── incident_response_guide.md
│   └── ai_security_guide.md
└── archive/                     # Obsolete documentation
    └── INDEX.md
```

## External Documentation

Some documentation files live in the repository root for visibility:

- `README.md` - Project overview and main entry point
- `QUICKSTART.md` - Quick start guide
- `SECURITY.md` - Security policy
- `ROADMAP.md` - Project roadmap
- `COMPLIANCE_CHECKLIST.md` - Compliance tracking

## Need Help?

- Check the [Troubleshooting Guide](guides/troubleshooting.md)
- Review the [FAQ](guides/faq.md)
- Open an issue on GitHub
- Consult the [archived documentation](archive/INDEX.md) for historical context

## Last Updated

This documentation structure was established following ADR-002 (2025-12-12).
