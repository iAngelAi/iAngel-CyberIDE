# Contributing Guide

## Welcome

Thank you for your interest in contributing to CyberIDE! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/iAngel-CyberIDE.git
cd iAngel-CyberIDE
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/iAngelAi/iAngel-CyberIDE.git
```

4. Set up development environment: See [Installation Guide](installation.md)

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions/fixes

### 2. Make Changes

Follow our [Development Guide](development.md) and coding standards.

### 3. Write Tests

All code changes must include tests:

```bash
# Frontend tests
npm run test:watch

# Backend tests
pytest -v
```

Test coverage must be above 80%.

### 4. Lint and Format

```bash
# Frontend
npm run lint
npm run lint -- --fix

# Backend
ruff check --fix .
ruff format .
```

### 5. Commit Changes

Use conventional commit format:

```bash
git commit -m "feat: Add neural region visualization"
git commit -m "fix: Resolve WebSocket reconnection issue"
git commit -m "docs: Update installation guide"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `style:` - Formatting
- `chore:` - Maintenance
- `perf:` - Performance improvement

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Create a pull request on GitHub with:
- Clear title and description
- Link to related issues
- Screenshots for UI changes
- Test results

## Coding Standards

### TypeScript

- Strict mode enabled (see `.github/standards/tsconfig.strict.json`)
- Use Zod for validation
- NO `any` types
- NO type casting with `as`
- Proper error handling

### Python

- Type hints required
- Follow `.github/standards/pyproject.strict.toml`
- Use Pydantic for models
- Structured logging
- NO generic exceptions

### Documentation

- Follow [ADR-002: Documentation Standards](../adr/ADR-002-documentation-standards.md)
- No emojis in technical documentation
- Relative paths only
- Clear, professional language

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows project standards
- [ ] Tests pass locally
- [ ] Test coverage above 80%
- [ ] Linters pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Screenshots
(If applicable)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Follows coding standards
- [ ] No breaking changes (or documented)
```

## Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Security

Report security vulnerabilities privately to security@iangelai.com. See [SECURITY.md](../../SECURITY.md).

## Documentation Contributions

Documentation improvements are highly valued:

- Fix typos and unclear explanations
- Add examples and tutorials
- Translate content
- Improve organization

## Community

- [GitHub Discussions](https://github.com/iAngelAi/iAngel-CyberIDE/discussions)
- [Issues](https://github.com/iAngelAi/iAngel-CyberIDE/issues)

## Questions?

- Check [documentation](../README.md)
- Ask in discussions
- Open an issue

Thank you for contributing!
