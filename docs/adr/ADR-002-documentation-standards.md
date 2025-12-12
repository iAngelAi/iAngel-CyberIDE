# ADR-002: Documentation Standards and Best Practices

## Status

Accepted

## Date

2025-12-12

## Context

The CyberIDE project has accumulated various documentation files with inconsistent formatting, language usage, and professional standards. Key issues include:

1. Use of emojis in technical documentation reducing professional appearance
2. Hardcoded absolute paths making documentation non-portable
3. Inconsistent language usage (mixing French and English)
4. Duplicate and overlapping content across multiple files
5. Outdated timestamps and references
6. Lack of clear documentation hierarchy and index

As the project matures and aims for enterprise adoption, documentation must reflect industry best practices for maintainability, professionalism, and accessibility.

## Decision

We adopt the following documentation standards for the CyberIDE project:

### 1. Professional Formatting

**No emojis in technical documentation.** Emojis are excluded from:
- Architecture Decision Records (ADRs)
- API documentation
- Security policies
- Compliance documentation
- Developer guides
- Technical specifications

Emojis may be used sparingly in:
- User-facing guides (README.md introduction only)
- Marketing materials
- Community engagement content

**Rationale:** Technical documentation must maintain professional credibility for enterprise adoption, audits, and compliance reviews.

### 2. Path References

All file path references must be:
- **Relative** to the repository root (e.g., `docs/guides/setup.md`)
- **Platform-agnostic** (use forward slashes `/`)
- **Never hardcoded** with absolute paths or user-specific directories

**Exception:** Command-line examples may use `.` or `$(pwd)` for current directory.

### 3. Language Usage

- **French:** User-facing documentation, product vision, roadmap
- **English:** Technical documentation, code comments, API references, ADRs, security documentation
- **Consistency:** Each document must use a single language throughout

**Rationale:** English is the lingua franca of software development, enabling collaboration with international contributors. French is retained for user-facing content to serve the primary Québec market.

### 4. Timestamps

- **ADRs:** Include decision date in ISO 8601 format (YYYY-MM-DD)
- **Reports:** Include generation timestamp
- **Guides:** Avoid specific dates; use version numbers or "Last Updated" with auto-generation
- **Changelogs:** Follow Keep a Changelog format with dates

**Avoid:** Outdated dates that quickly become misleading.

### 5. Documentation Structure

```
/
├── README.md                 # Main entry point (bilingual intro)
├── QUICKSTART.md            # Single consolidated quick start guide
├── SECURITY.md              # Security policy and compliance
├── ROADMAP.md               # Project roadmap (French)
├── docs/
│   ├── README.md            # Documentation index
│   ├── guides/              # User and developer guides
│   │   ├── installation.md
│   │   ├── development.md
│   │   └── deployment.md
│   ├── adr/                 # Architecture Decision Records
│   │   ├── ADR-001-*.md
│   │   └── ADR-002-*.md
│   ├── reports/             # Test reports, metrics
│   ├── security/            # Security guides and procedures
│   └── archive/             # Obsolete documentation with index
│       └── INDEX.md         # Explains what's archived and why
```

### 6. Content Consolidation

- **Eliminate duplication:** Consolidate overlapping guides
- **Single source of truth:** One canonical document per topic
- **Cross-references:** Use links instead of copying content
- **Archive obsolete content:** Don't delete; move to archive with explanation

### 7. Markdown Best Practices

- Use ATX-style headers (`# Header`)
- Include table of contents for documents >100 lines
- Use code fences with language identifiers
- Use tables for structured data
- Use blockquotes for warnings/notes
- Maximum line length: No hard limit (let editors wrap)

### 8. Documentation Review

All documentation changes must:
- Pass linting (markdownlint)
- Be reviewed for technical accuracy
- Maintain consistency with these standards
- Update the docs/README.md index if structure changes

## Consequences

### Positive

- **Professional credibility** for enterprise adoption
- **Portability** across development environments
- **Maintainability** with clear structure and standards
- **Accessibility** for international contributors
- **Compliance readiness** with professional documentation
- **Reduced confusion** from duplicate/outdated content

### Negative

- **Initial effort** required to update existing documentation
- **Ongoing discipline** needed to maintain standards
- **Some content requires translation** when restructuring

### Mitigation

- Phased approach: Update high-priority docs first
- Create templates for common document types
- Add documentation linting to CI/CD pipeline
- Document standards in contribution guidelines

## Alternatives Considered

### Keep emojis everywhere
**Rejected:** Unprofessional for enterprise and compliance documentation.

### All English documentation
**Rejected:** Loses connection with Québec market and Loi 25 compliance context.

### No standards, freestyle documentation
**Rejected:** Leads to technical debt, confusion, and poor maintainability.

## References

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [Write the Docs Best Practices](https://www.writethedocs.org/guide/writing/style-guides/)
- ADR-001: Logging Strategy (existing project ADR)

## Implementation

This ADR will be implemented through:
1. Immediate update of existing documentation to remove emojis and absolute paths
2. Consolidation of duplicate quick start guides
3. Creation of docs/README.md index
4. Archiving of obsolete content with explanation
5. Update of contribution guidelines to reference these standards
