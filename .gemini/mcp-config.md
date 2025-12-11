# Configuration MCP pour Gemini CLI — CyberIDE

> **Version** : 1.0.0  
> **Dernière mise à jour** : 2025-12-10  
> **Projet** : iAngel-CyberIDE  
> **Configuré par** : Claude (via Docker MCP Gateway)

---

## 🎯 Vue d'ensemble

Cette configuration MCP est optimisée pour le développement **Production-First** de CyberIDE,
un IDE neural avec visualisation 3D. Elle respecte les standards stricts définis dans `CLAUDE.md` :

- ✅ **Typage strict** : Pas de `any`, validation Pydantic V2 / Zod
- ✅ **Audit-First** : Analyse avant modification
- ✅ **Tests obligatoires** : Coverage > 80%
- ✅ **Sécurité** : Scan automatique des vulnérabilités

---

## 📦 Serveurs MCP Actifs

### Priorité CRITIQUE — Documentation & Core

| Serveur | Outils | Usage |
|---------|--------|-------|
| `context7` | 2 | Docs à jour Three.js, React, FastAPI, Pydantic |
| `github-official` | 20 | PR, Issues, Code Review, Search |
| `mcp-code-interpreter` | 1 | REPL Python persistant |

### Priorité HAUTE — Qualité Code

| Serveur | Outils | Usage |
|---------|--------|-------|
| `semgrep` | 8 | Scan sécurité statique, AST analysis |
| `mcp-python-refactoring` | 9 | Refactoring guidé, TDD, coverage |
| `ast-grep` | 1 | Recherche structurelle polyglot |

### Priorité MOYENNE — DevOps & Productivité

| Serveur | Outils | Usage |
|---------|--------|-------|
| `sequentialthinking` | 1 | Réflexion structurée, anti-reward-hacking |
| `npm-sentinel` | 19 | Analyse packages NPM, vulnérabilités |
| `node-code-sandbox` | 7 | Sandbox Docker JS/TS isolé |
| `playwright-mcp-server` | 32 | Tests E2E, screenshots, browser automation |

**Total : 100 outils MCP**

---

## 🔧 Configuration Requise

### Prérequis

```bash
# Docker Desktop 4.40+ avec MCP Toolkit activé
docker --version  # >= 24.0

# Gemini CLI
npm install -g @google/gemini-cli
gemini --version  # >= 1.2.0
```

### ~/.gemini/settings.json

```json
{
  "security": {
    "auth": { "selectedType": "gemini-api-key" },
    "folderTrust": { "enabled": true }
  },
  "mcpServers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    }
  },
  "general": {
    "previewFeatures": true,
    "sessionRetention": { "enabled": true },
    "enablePromptCompletion": true
  },
  "context": { "loadMemoryFromIncludeDirectories": true }
}
```

---

## 🚀 Commandes d'Activation

### Activation Initiale (une seule fois)

```bash
# Priorité CRITIQUE
docker mcp add context7 --activate
docker mcp add github-official --activate
docker mcp add mcp-code-interpreter --activate

# Priorité HAUTE
docker mcp add semgrep --activate
docker mcp add mcp-python-refactoring --activate
docker mcp config set ast-grep path="/Volumes/DevSSD/iAngel-CyberIDE"
docker mcp add ast-grep --activate

# Priorité MOYENNE
docker mcp add sequentialthinking --activate
docker mcp add npm-sentinel --activate
docker mcp add node-code-sandbox --activate
docker mcp config set playwright-mcp-server data="/tmp/playwright-data"
docker mcp add playwright-mcp-server --activate
```

### Vérification

```bash
gemini
# Dans Gemini CLI :
/mcp
# Devrait afficher tous les serveurs CONNECTED
```

---

## 📖 Guide d'Utilisation par Cas

### 1. Obtenir la documentation à jour

```
@context7 Comment utiliser useFrame dans @react-three/fiber ?
```

### 2. Analyser la sécurité du code

```
@semgrep Scanne neural_cli/main.py pour les vulnérabilités
```

### 3. Refactoring Python guidé

```
@mcp-python-refactoring Analyse neural_cli/ et suggère des améliorations
```


### 4. Recherche structurelle de patterns

```
# Trouver tous les usages de "any" en TypeScript
@ast-grep pattern="any" lang="typescript"

# Trouver les imports non typés
@ast-grep pattern="import $X from '$Y'" lang="typescript"
```

### 5. Analyse packages NPM

```
@npm-sentinel Vérifie les vulnérabilités de three et @react-three/fiber
```

### 6. Tests E2E avec Playwright

```
@playwright Navigue vers localhost:5173 et prends un screenshot du brain 3D
```

### 7. Exécution Python isolée

```
@mcp-code-interpreter
import pandas as pd
df = pd.read_csv("test_results.csv")
print(df.describe())
```

### 8. Résolution de problèmes complexes

```
@sequentialthinking Analyse le problème de performance du rendu 60 FPS
```

---

## ⚠️ Serveurs Non Configurés

### SonarQube (optionnel)

Nécessite un token SonarQube Cloud ou Server :

```bash
docker mcp secret set sonarqube.token=<VOTRE_TOKEN>
docker mcp config set sonarqube url="https://sonarcloud.io"  # ou votre instance
docker mcp config set sonarqube org="votre-org"  # pour SonarCloud
docker mcp add sonarqube --activate
```

---

## 🔒 Sécurité

### Secrets Gérés

Les secrets sont stockés de manière sécurisée par Docker MCP Gateway :

- `github.personal_access_token` — Pour github-official
- `sonarqube.token` — Pour sonarqube (optionnel)

### Bonnes Pratiques

1. **Ne jamais commiter** les tokens dans le code
2. **Rotation régulière** des tokens (90 jours)
3. **Permissions minimales** (least privilege)

---

## 📊 Correspondance avec les Standards CyberIDE

| Standard CLAUDE.md | Serveur MCP | Validation |
|--------------------|-------------|------------|
| Typage strict (no `any`) | `ast-grep`, `semgrep` | Recherche patterns interdits |
| Validation Zod/Pydantic | `context7` | Docs à jour des schémas |
| Tests > 80% | `mcp-python-refactoring` | Analyse coverage |
| Audit-First | `sequentialthinking` | Réflexion avant action |
| Sécurité | `semgrep`, `npm-sentinel` | Scan vulnérabilités |

---

## 🔄 Mise à Jour

Pour mettre à jour les serveurs MCP :

```bash
docker mcp update  # Met à jour tous les serveurs
```

---

## 📞 Support

- **Docker MCP Toolkit** : https://docs.docker.com/mcp/
- **Gemini CLI** : https://geminicli.com/docs/
- **Context7** : https://context7.com/docs/

---

*Configuration générée automatiquement par Claude pour le projet CyberIDE.*
