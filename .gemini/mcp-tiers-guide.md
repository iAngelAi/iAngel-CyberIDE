# 🎛️ Guide d'Activation des Tiers MCP — CyberIDE

> **Configuration**: Lab AI Senior Pattern  
> **Date**: 2025-12-10  
> **Serveurs**: 6 | **Outils**: 65 (3 actifs par défaut)

---

## 📊 Architecture des Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: ALWAYS ON                                    [3 outils] │
│   ├── context7 (2)        → Docs Three.js/React/FastAPI        │
│   └── sequentialthinking (1) → Réflexion anti-reward-hacking   │
├─────────────────────────────────────────────────────────────────┤
│ TIER 2: ON-DEMAND (code analysis)                   [29 outils] │
│   ├── github-official (20) → @github pour activer              │
│   ├── ast-grep (1)         → @ast-grep pour activer            │
│   └── semgrep (8)          → @semgrep pour activer             │
├─────────────────────────────────────────────────────────────────┤
│ TIER 3: CI/TESTING (automation)                     [32 outils] │
│   └── playwright-mcp-server (32) → @playwright pour activer    │
├─────────────────────────────────────────────────────────────────┤
│ TIER 4: SANDBOXED (execution)                        [1 outil]  │
│   └── mcp-code-interpreter (1) → @code-interpreter pour activer│
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Deny-Lists Actives (Sécurité Lab Senior)

### Outils BLOQUÉS

| Serveur | Outil Bloqué | Raison |
|---------|--------------|--------|
| github-official | `delete_file` | Pas de suppression auto |
| github-official | `merge_pull_request` | Requiert review humaine |
| playwright-mcp-server | `playwright_upload_file` | Risque exfiltration |

### Outils avec CONFIRMATION

| Serveur | Outil |
|---------|-------|
| github-official | `create_pull_request` |
| github-official | `push_files` |

---

## ⏱️ Timeouts

| Serveur | Startup | Execution |
|---------|---------|-----------|
| context7 | 15s | 30s |
| sequentialthinking | 10s | 60s |
| github-official | 20s | 45s |
| ast-grep | 10s | 30s |
| semgrep | 30s | 120s |
| playwright-mcp-server | 60s | 180s |
| mcp-code-interpreter | 20s | 60s |

---

## 📦 Token Budgets

- **Tool Output**: 4,096 tokens/outil
- **Context Window**: 100,000 tokens
- **Max Output**: 8,192 tokens

---

## 🎯 Workflows

### Dev Normal (TIER 1)
```
"Explique useBrainState" → context7 + sequentialthinking
```

### Code Review (TIER 1+2)
```
"@github-official @semgrep review PR #42"
```

### Tests E2E (TIER 1+3)
```
"@playwright teste Brain3D"
```

### Data Analysis (TIER 1+4)
```
"@mcp-code-interpreter analyse ce CSV"
```
