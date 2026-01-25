# Mission 001: Implement CI/CD Pipeline for Neural Core Backend

**Priority:** High
**Status:** Ready to Start

## Context
The Neural Core backend (`neural_cli`) is now critical for the "Universal" feature. While local tests exist, there is no automated CI pipeline ensuring they pass on every commit.

## Objectives
Create a GitHub Actions workflow `.github/workflows/backend-ci.yml` that:
1. Sets up Python 3.10+ environment.
2. Installs dependencies from `requirements.txt`.
3. Runs `pytest tests/ --cov=neural_cli`.
4. Fails the build if coverage drops below 80%.

## Definition of Done (DoD)
- [ ] Workflow file created and active
- [ ] Pipeline runs successfully on PRs
- [ ] Branch protection rules updated to require this check
