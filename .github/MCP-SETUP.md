MCP-SETUP.md# MCP Configuration Guide for iAngel-Labs Multi-Agent System

## Overview

This document describes the Model Context Protocol (MCP) setup for the iAngel-Labs multi-agent development system. The configuration uses **Google Cloud Platform**, **Azure DevOps**, and **DigitalOcean** instead of AWS.

## Architecture

### Lead Agent Orchestration
- **Lead Agent**: `architecte-principal` acts as the orchestrator
- **Sub-agents**: 11 specialized agents with domain-specific capabilities
- **Discovery**: Dynamic tool discovery at initialization
- **Execution**: Parallel execution enabled for efficiency

## MCP Servers Configuration

### 1. Google Cloud Platform (GCP)
**Purpose**: Cloud infrastructure management (AWS replacement)

**Services**:
- Compute Engine
- Cloud Storage  
- Cloud Functions
- Cloud Run
- BigQuery

**Agents**: DevOps/SRE, Architect, Data Engineer, MLOps

**Setup**:
```bash
npm install @googleapis/gcloud-mcp
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### 2. Azure DevOps
**Purpose**: CI/CD workflows, work items, builds, test plans

**Agents**: DevOps/SRE, Agile Coach, TPM, QA Automation

**Setup**:
```bash
git clone https://github.com/microsoft/azure-devops-mcp
cd azure-devops-mcp && npm install
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-personal-access-token"
```

### 3. DigitalOcean
**Purpose**: App Platform deployment and management

**Agents**: DevOps/SRE, Full-Stack Developer

**Setup**:
```bash
npm install @digitalocean/mcp
export DIGITALOCEAN_API_TOKEN="your-do-token"
```

### 4. BigQuery
**Purpose**: Data analysis and querying

**Agents**: Data Engineer, MLOps, Architect

**Setup**:
```bash
npm install mcp-bigquery-server
export BIGQUERY_PROJECT_ID="your-gcp-project"
```

### 5. GitHub
**Purpose**: Repository management, PRs, issues

**Agents**: Architect, Full-Stack Dev, Backend Engineer, QA, Agile Coach

**Setup**:
```bash
npm install @modelcontextprotocol/server-github
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token"
```

### 6. Additional Servers
- **SQLite**: Database operations
- **Filesystem**: File system access (restricted)
- **Puppeteer**: Browser automation for UI/UX and QA
- **GitLab** (optional): Alternative Git repository
- **Google Analytics**: Product analytics for UX/UI

## Agent-to-MCP Mapping

| Agent | MCP Servers |
|-------|-------------|
| **3DEngineer** | filesystem, puppeteer |
| **ConcepteurUXUI** | puppeteer, google-analytics, github |
| **architecte-principal** | github, google-cloud, bigquery, gitlab |
| **chef-produit-technique-tpm** | azure-devops, google-analytics |
| **coach-agile** | github, azure-devops |
| **developpeur-fullstack** | github, digitalocean, database-sqlite, gitlab |
| **ingenieur-backend-mcp** | github, database-sqlite, gitlab |
| **ingenieur-devops-sre** | google-cloud, azure-devops, digitalocean |
| **ingenieur-donnees** | google-cloud, bigquery, database-sqlite |
| **ingenieur-mlops** | google-cloud, bigquery |
| **ingenieur-qa-automation** | github, azure-devops, puppeteer |
| **specialiste-securite** | github, google-cloud, azure-devops |

## Security Configuration

### Authentication
- **OAuth Scopes**: Minimal required permissions
- **Token Lifetime**: Short-lived tokens only
- **Rotation**: Regular automatic rotation

### Access Control
- **Principle**: Least privilege
- **Per-Agent Permissions**: Each agent has specific server access
- **Audit Logging**: All MCP interactions logged

### File System Security
- **Allowed Directories**: `${WORKSPACE_PATH}`, `${PROJECT_ROOT}` only
- **Default Mode**: Read-only unless explicitly granted write

## Registry Configuration

**Registry URL**: `https://registry.iangel-labs.com/mcp/allowed-servers`

**Allowlist Enabled**: Yes

**Approved Servers**:
- github
- google-cloud
- azure-devops  
- digitalocean
- bigquery
- database-sqlite
- filesystem
- puppeteer

## Enterprise MCP Settings

**Location**: GitHub Enterprise → AI Controls → MCP

**Settings**:
1. ✅ MCP servers in Copilot: **Enabled everywhere**
2. ✅ MCP Registry URL: Configured
3. ⚙️ Access restrictions: Allowlist-based

## Installation Steps

### 1. Install Core Dependencies
```bash
# Install Node.js and npm
npm install -g npx

# Clone MCP servers
git clone https://github.com/microsoft/azure-devops-mcp
```

### 2. Set Environment Variables
Create a `.env` file:
```bash
# GCP
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-credentials.json
GCP_PROJECT_ID=your-project

# Azure DevOps
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-pat-token

# DigitalOcean
DIGITALOCEAN_API_TOKEN=your-do-token

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token

# Paths
WORKSPACE_PATH=/path/to/workspace
PROJECT_ROOT=/path/to/project
```

### 3. Configure Agents
Each agent automatically discovers available MCP tools at initialization. No manual configuration needed per agent.

### 4. Test Configuration
```bash
# Test GCP connection
gcloud auth list

# Test Azure DevOps
az devops project list

# Test DigitalOcean
doctl auth list
```

## Usage Examples

### DevOps Agent with GCP
```
Agent: "Deploy the application to Cloud Run"
MCP: Uses google-cloud server → Cloud Run API
```

### Data Engineer with BigQuery
```
Agent: "Query user analytics from last 30 days"
MCP: Uses bigquery server → Executes SQL query
```

### QA Automation with Puppeteer
```
Agent: "Test the checkout flow on staging"
MCP: Uses puppeteer server → Automates browser testing
```

## Troubleshooting

### MCP Server Not Found
- Check if server is in allowlist
- Verify npm package installation
- Check environment variables

### Authentication Errors
- Verify tokens are not expired
- Check credential file paths
- Ensure proper OAuth scopes

### Permission Denied
- Review agent-specific permissions
- Check file system access restrictions
- Verify least-privilege configuration

## Best Practices

1. **Token Security**: Never commit tokens to version control
2. **Scope Minimization**: Grant only required permissions
3. **Regular Audits**: Review MCP access logs weekly
4. **Server Updates**: Keep MCP servers updated
5. **Testing**: Test MCP connections before deployment

## Resources

- [MCP Specification](https://github.com/modelcontextprotocol/registry)
- [Google Cloud MCP](https://github.com/googleapis/gcloud-mcp)
- [Azure DevOps MCP](https://github.com/microsoft/azure-devops-mcp)
- [DigitalOcean MCP](https://github.com/digitalocean/digitalocean-mcp)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)

## Support

For issues or questions:
1. Check the configuration file: `.github/mcp-configuration.json`
2. Review agent logs for MCP connection errors
3. Consult enterprise MCP settings in GitHub

---

**Last Updated**: December 3, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
