# Mission 002: Add Visual Regression Tests for 3D Brain

**Priority:** Medium
**Status:** Ready to Start

## Context
The 3D Brain visualization is the core USP of CyberIDE. We recently added "Glitch" effects and dynamic coloring. We need to ensure future updates don't break these visuals.

## Objectives
Utilize the existing `playwright-mcp-server` integration to:
1. Create a visual test suite in `src/__tests__/e2e/visual.spec.ts`.
2. Capture screenshots of the Brain in 'Healthy', 'Critical', and 'Offline' states.
3. Compare them against baselines to detect visual regressions.

## Definition of Done (DoD)
- [ ] Playwright configured for visual comparison
- [ ] Baselines committed for all 3 states
- [ ] Test command `npm run test:e2e` added
