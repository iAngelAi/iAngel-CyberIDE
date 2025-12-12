# Documentation Archive Index

## Purpose

This archive contains documentation that is no longer current but is preserved for historical reference. Files are archived rather than deleted to maintain project history and context.

## Archive Policy

Documentation is archived when:
- It describes features or approaches that have been superseded
- It contains outdated information that could mislead current contributors
- It has been consolidated into other documentation
- It refers to abandoned design directions or prototypes

## Archived Content

### Legacy Agent Definitions (Archived: 2025-12-12)

**Location:** `docs/archive/legacy_agents/`

**Reason:** These agent definition files have been superseded by the current multi-agent architecture and are no longer used. The active agent definitions are now located in `.github/agents/`.

**Historical Value:** Documents the evolution of the agent-based development approach and early design decisions.

**Files:**
- `3DEngineer.md` - Early 3D engineer agent specification
- `ConcepteurUXUI.md` - UX/UI designer agent specification
- `architecte-principal.agent.md` - Principal architect agent
- `chef-produit-technique-tpm.agent.md` - Technical product manager agent
- `coach-agile.agent.md` - Agile coach agent
- `developpeur-fullstack.agent.md` - Full-stack developer agent
- `docXpert.agent.md` - Documentation expert agent (superseded by current DocXpert)
- `ingenieur-backend-mcp.agent.md` - Backend MCP engineer agent
- `ingenieur-devops-sre.agent.md` - DevOps/SRE engineer agent
- `ingenieur-donnees.agent.md` - Data engineer agent
- `ingenieur-mlops.agent.md` - MLOps engineer agent
- `ingenieur-qa-automation.agent.md` - QA automation engineer agent
- `specialiste-securite-conformite.agent.md` - Security/compliance specialist agent

### Vision and Analysis Documents (Archived: 2025-12-12)

**Location:** `docs/archive/`

**Files:**
- `CYBERIDE_VISION_ANALYSIS_OLD.md` - Original vision and analysis document
- `EXECUTIVE_SUMMARY_OLD.md` - Original executive summary
- `NEURAL_MANIFESTO.md` - Original neural core philosophy document
- `NEURAL_CORE_SUMMARY.md` - Summary of neural core features

**Reason:** These documents were exploratory and have been superseded by the current README.md and project documentation. The vision has evolved and been refined since these early documents.

**Historical Value:** Captures the initial product vision and early decision-making process.

### Detailed Setup Guides (Archived: 2025-12-12)

**Location:** `docs/archive/`

**Files:**
- `NEURAL_QUICKSTART.md` - Original neural core quick start guide
- `NEURAL_CORE_GUIDE.md` - Detailed neural core setup guide
- `SETUP.md` - Original setup instructions

**Reason:** Consolidated into a single comprehensive QUICKSTART.md in the repository root. The multiple overlapping guides created confusion about which to follow.

**Historical Value:** Contains detailed context about early development environment setup approaches.

### Technical Reports (Moved to docs/reports/)

**Location:** `docs/reports/`

**Note:** The following files have been moved to a dedicated reports directory rather than archived, as they contain useful historical data:
- `TEST_EXECUTION_REPORT.md`
- `TEST_SUITE_SUMMARY.md`
- `IMPLEMENTATION_SUMMARY.md`
- `IMPLEMENTATION_LOCKFILES.md`
- `BACKEND_REGION_SYNC.md`
- `BUILD_NOTES.md`

These remain accessible for reference but are not part of the primary documentation structure.

## Accessing Archived Content

Archived content is read-only and should not be modified. If you need to reference historical decisions:

1. Check this INDEX.md first to understand why content was archived
2. Review the archived files in their context (date, project phase)
3. Consult current documentation for up-to-date information
4. Create an ADR if archived decisions need to be revisited

## Related Documentation

- Current agent definitions: `.github/agents/`
- Current project vision: `README.md`
- Architecture decisions: `docs/adr/`
- Development roadmap: `ROADMAP.md`

## Questions?

If you believe archived content should be restored or if you have questions about why something was archived, please:
1. Review the related ADRs in `docs/adr/`
2. Check the git history for the file
3. Open a discussion with the team
