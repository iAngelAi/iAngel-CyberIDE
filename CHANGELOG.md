# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ADR-002: Documentation Standards and Best Practices
- Comprehensive documentation structure in `docs/`
- Documentation index at `docs/README.md`
- Archive policy and index at `docs/archive/INDEX.md`
- Installation guide at `docs/guides/installation.md`
- Development guide at `docs/guides/development.md`
- Troubleshooting guide at `docs/guides/troubleshooting.md`
- Contributing guide at `docs/guides/contributing.md`
- CHANGELOG.md following Keep a Changelog format

### Changed
- Reorganized documentation into logical structure
- Moved test reports to `docs/reports/`
- Archived obsolete documentation to `docs/archive/`
- Removed emojis from all technical documentation
- Removed hardcoded absolute paths from documentation
- Consolidated QUICKSTART.md with improved structure
- Updated all documentation dates to current or removed them
- Standardized language usage (French for user docs, English for technical)

### Removed
- Emojis from README.md, ROADMAP.md, ENVIRONMENT_SETUP.md
- Emojis from COMPLIANCE_CHECKLIST.md, CLAUDE.md, SECURITY.md
- Emojis from all security documentation files
- Hardcoded paths like `/Users/felixlefebvre/CyberIDE`
- Duplicate content from multiple quick start guides

### Deprecated
- NEURAL_QUICKSTART.md (archived, content merged into QUICKSTART.md)
- NEURAL_CORE_GUIDE.md (archived)
- NEURAL_CORE_SUMMARY.md (archived)
- NEURAL_MANIFESTO.md (archived)
- SETUP.md (archived, content in QUICKSTART.md and docs/guides/)

## [0.0.0] - 2024-12-12

### Initial Release

This represents the baseline before documentation restructuring.

#### Core Features
- React 19 + TypeScript frontend with 3D neural brain visualization
- FastAPI + Python backend with real-time WebSocket communication
- Multi-agent architecture with 13 specialized agents
- Test-driven development with comprehensive test suites
- Security-first design with compliance for Loi 25, PIPEDA, and RGPD

#### Documentation (Before Restructuring)
- README.md with project overview
- Multiple overlapping setup guides
- Test execution reports in root directory
- Security and compliance documentation
- Agent definition files in multiple locations

[Unreleased]: https://github.com/iAngelAi/iAngel-CyberIDE/compare/v0.0.0...HEAD
[0.0.0]: https://github.com/iAngelAi/iAngel-CyberIDE/releases/tag/v0.0.0
