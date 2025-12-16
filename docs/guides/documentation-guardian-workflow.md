# Documentation Guardian Workflow

## Overview

The **Documentation Guardian** is an automated GitHub Actions workflow that prevents **Code Rot** by ensuring code changes are accompanied by appropriate documentation updates.

**Workflow File**: `.github/workflows/doc-guardian.yml`

## Purpose

In accordance with [ADR-002 Documentation Standards](../adr/ADR-002-documentation-standards.md), this workflow enforces the principle that:

> Code changes MUST be reflected in documentation to maintain alignment between implementation and documentation.

## How It Works

### Automatic Checks on Pull Requests

The workflow automatically runs on every Pull Request targeting `main` or `develop` branches and performs the following checks:

1. **Detects Changed Files**: Identifies all `.py` and `.ts`/`.tsx` files modified in the PR
2. **Checks for Documentation**: Verifies if any `.md` files were also modified
3. **Triggers Warning**: If code files changed WITHOUT documentation updates, the workflow:
   - Posts a detailed comment on the PR explaining the issue
   - **Fails the status check** (prevents merge if branch protection is enabled)
   - Lists all modified code files
   - Provides recommendations for documentation updates

### Manual Repository-Wide Check

A manual trigger (`workflow_dispatch`) allows running a comprehensive documentation audit:

```bash
# Via GitHub UI:
Actions → Documentation Guardian → Run workflow → Enable "Check entire repository"
```

This mode:
- Scans ALL Python and TypeScript files in the repository
- Identifies directories missing README.md files
- Provides statistics on code-to-documentation ratio
- Suggests areas needing documentation attention

## Workflow Triggers

### Pull Request Trigger

```yaml
on:
  pull_request:
    branches: [ main, develop ]
    types: [ opened, synchronize, reopened ]
```

**When it runs**:
- New PR opened
- New commits pushed to existing PR
- Closed PR reopened

### Manual Dispatch Trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      check_full_repo:
        description: 'Check entire repository for documentation gaps'
        type: choice
        options:
          - 'true'
          - 'false'
```

**When to use**:
- Regular documentation audits (recommended monthly)
- Before major releases
- After significant refactoring
- When onboarding new team members

## Permissions

The workflow uses minimal required permissions following the **Principle of Least Privilege**:

```yaml
permissions:
  contents: read          # Read repository files
  pull-requests: write    # Post comments on PRs
  issues: write          # Update issue comments
```

**Security Note**: The workflow uses `${{ secrets.GITHUB_TOKEN }}` which is automatically provided by GitHub Actions and scoped to the repository. No additional secrets required.

## Behavior Details

### Scenario 1: Code + Documentation Changed ✅

**Result**: Workflow PASSES

```
✅ Documentation Guardian: PASSED

This PR includes both code and documentation changes.
Thank you for maintaining documentation quality!
```

### Scenario 2: Code Changed, No Documentation ⚠️

**Result**: Workflow FAILS with detailed comment

The workflow posts a comment containing:
- Summary of changed files (Python, TypeScript, Markdown counts)
- List of all modified code files
- Recommendations for documentation updates
- Links to relevant documentation standards
- Instructions for legitimate exceptions

**Example Comment**:

```markdown
## ⚠️ Documentation Guardian Alert

This Pull Request modifies code files but does not include any documentation updates.

### Changed Files Summary
- **Python files**: 3
- **TypeScript files**: 2
- **Documentation files**: 0

### Recommendations
1. Update README files in modified directories
2. Update API documentation if APIs changed
3. Create/update ADR for architectural changes
4. Add CHANGELOG.md entry
5. Update user guides if features changed
```

### Scenario 3: Documentation-Only Changes ℹ️

**Result**: Workflow SKIPPED

```
ℹ️  Documentation Guardian: SKIPPED

No Python or TypeScript files were modified in this PR.
Documentation-only changes do not require this check.
```

## Bypassing the Check

### Legitimate Cases for No Documentation

Some changes legitimately don't require documentation updates:

1. **Internal Refactoring**: No API or behavior changes
2. **Test-Only Changes**: Adding/updating unit tests
3. **Typo Fixes**: Correcting comments or variable names
4. **Build Configuration**: Changes to build scripts with no user impact
5. **Dependency Updates**: Package version bumps with no breaking changes

### How to Bypass

If your PR falls into a legitimate exception:

1. **Add a comment** on the PR explaining why documentation is not needed
2. **Request review** from a maintainer who can override the check
3. **Document your reasoning** clearly for future reference

**Example Comment**:
```
This PR only refactors internal helper functions without changing any public APIs.
No documentation update is required as there are no user-facing changes.
```

## Integration with Branch Protection

### Recommended Setup

To enforce documentation standards, configure branch protection rules:

1. Navigate to: **Settings → Branches → Branch protection rules**
2. Add rule for `main` and `develop` branches
3. Enable: ✅ **Require status checks to pass before merging**
4. Select: ✅ **Check Documentation Coverage**

This ensures PRs cannot be merged if documentation is missing.

### Optional: Require Reviews

For stricter control:
- ✅ **Require pull request reviews before merging**
- Set **Required approving reviews**: 1 or 2
- Allow maintainers to approve exceptions

## Monitoring and Metrics

### View Workflow Runs

```bash
# Via GitHub UI
Actions → Documentation Guardian

# Via GitHub CLI
gh run list --workflow=doc-guardian.yml
```

### Key Metrics to Track

- **Pass Rate**: Percentage of PRs passing on first attempt
- **Documentation Coverage**: Files with corresponding docs
- **Manual Checks**: Frequency of repository-wide audits

## Troubleshooting

### Workflow Not Running

**Check**:
1. Workflow file syntax is valid
2. PR targets `main` or `develop` branch
3. Repository has Actions enabled

### False Positives

**Issue**: Workflow fails but documentation WAS updated

**Solution**:
1. Ensure `.md` files are committed and pushed
2. Check file paths are not excluded by `.gitignore`
3. Verify changes are in the same commit/PR

### Comment Not Posted

**Issue**: Workflow runs but no PR comment appears

**Check**:
1. Workflow has `pull-requests: write` permission
2. `GITHUB_TOKEN` is available (automatically provided)
3. Check Actions logs for error messages

## Integration with DocXpert Agent

The Documentation Guardian workflow complements the **DocXpert agent** (`.github/agents/DocXpert.agent.md`):

- **Guardian (Automated)**: Prevents code merging without docs
- **DocXpert (Manual)**: Provides expert documentation assistance

### Workflow Integration

When the Guardian fails:
1. Review the posted comment
2. Identify required documentation
3. Invoke DocXpert agent: `@DocXpert Please update documentation for [component]`
4. Review and commit DocXpert's changes
5. Push to PR to re-trigger Guardian

## Maintenance

### Regular Updates

**Monthly**:
- Run manual repository-wide check
- Review directories missing README files
- Update documentation based on findings

**Per Release**:
- Audit documentation completeness
- Update CHANGELOG.md
- Verify all ADRs are current

### Workflow Updates

When modifying the workflow:
1. Test changes in a feature branch
2. Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('.github/workflows/doc-guardian.yml'))"`
3. Run manual dispatch to test logic
4. Document changes in PR description

## Best Practices

### For Contributors

1. **Update docs with code**: Don't defer documentation
2. **Be specific**: Update the exact sections affected
3. **Test locally**: Review your changes before pushing
4. **Ask for help**: Tag DocXpert agent when unsure

### For Maintainers

1. **Enforce consistently**: Don't allow exceptions to become habit
2. **Review reasoning**: Evaluate bypass requests carefully
3. **Provide feedback**: Help contributors improve documentation
4. **Lead by example**: Maintain excellent documentation in your PRs

### For DevOps/SRE

1. **Monitor workflow health**: Check for consistent failures
2. **Adjust thresholds**: Tune detection logic as needed
3. **Update dependencies**: Keep workflow actions current
4. **Document incidents**: Track patterns in documentation gaps

## Security Considerations

### No Secrets Exposed

The workflow:
- Uses only `${{ secrets.GITHUB_TOKEN }}` (automatic, scoped)
- Does NOT require additional API keys
- Does NOT expose sensitive data in logs
- Follows GitHub Actions security best practices

### Permissions Scoped

Minimal permissions granted:
- `contents: read` - Only read access to files
- `pull-requests: write` - Only comment on PRs
- `issues: write` - Only update comments

### Safe Execution

- Runs in isolated GitHub-hosted runner
- No external network calls
- No custom scripts from untrusted sources
- Uses official GitHub actions only

## Related Documentation

- [ADR-002: Documentation Standards](../adr/ADR-002-documentation-standards.md)
- [DocXpert Agent Specification](../../.github/agents/DocXpert.agent.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [Contributing Guidelines](../../README.md#contributing)

## Support

### Questions or Issues

1. **Review this guide** and workflow comments
2. **Check workflow logs** in Actions tab
3. **Consult DocXpert agent** for documentation help
4. **Open an issue** with label `workflow` or `documentation`

### Feedback

We continuously improve this workflow. Submit feedback via:
- GitHub Issues with label `enhancement`
- PR with proposed changes to workflow
- Discussion in team retrospectives

---

**Last Updated**: 2025-12-16  
**Maintained by**: Ingénieur DevOps/SRE  
**Status**: Active
