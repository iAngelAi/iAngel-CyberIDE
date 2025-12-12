# Guide DevSecOps & CI/CD — CyberIDE

<div align="center">

**Version 1.0.0** | Décembre 2024

*"Shift Security Left: Integrate Security from Day One"*

</div>

---

## Vue d'Ensemble

Ce guide décrit l'intégration de la sécurité dans les pipelines CI/CD du projet CyberIDE, suivant les principes DevSecOps.

**Objectif:** Détecter et corriger les vulnérabilités le plus tôt possible dans le cycle de développement.

---

## Architecture du Pipeline de Sécurité

```
┌─────────────────────────────────────────────────────────────┐
│ DÉVELOPPEMENT LOCAL │
│ ├─ Pre-commit hooks (Gitleaks) │
│ ├─ Linters locaux (ESLint, Ruff) │
│ ├─ Tests unitaires + sécurité │
│ └─ IDE security plugins │
└────────────────────────┬────────────────────────────────────┘
 │ git push
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 1: CODE ANALYSIS (Parallèle) │
│ ├─ SAST - Static Application Security Testing │
│ │ └─ CodeQL (GitHub Advanced Security) │
│ │ └─ SonarQube / SonarCloud │
│ │ └─ Bandit (Python) │
│ ├─ Linting & Type Checking │
│ │ └─ ESLint + TypeScript Compiler │
│ │ └─ Ruff + mypy │
│ └─ Secrets Scanning │
│ └─ Gitleaks │
│ └─ TruffleHog │
└────────────────────────┬────────────────────────────────────┘
 │ if passed
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 2: DEPENDENCY ANALYSIS (Parallèle) │
│ ├─ SCA - Software Composition Analysis │
│ │ └─ npm audit │
│ │ └─ pip-audit │
│ │ └─ Snyk │
│ ├─ License Compliance │
│ │ └─ license-checker │
│ └─ SBOM Generation │
│ └─ Software Bill of Materials (CycloneDX) │
└────────────────────────┬────────────────────────────────────┘
 │ if passed
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 3: BUILD & TEST │
│ ├─ Build Application │
│ ├─ Unit Tests │
│ ├─ Integration Tests │
│ └─ Security Tests │
└────────────────────────┬────────────────────────────────────┘
 │ if passed
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 4: CONTAINER SECURITY (if applicable) │
│ ├─ Container Image Scanning (Trivy) │
│ ├─ Base Image Vulnerabilities │
│ └─ Container Best Practices (hadolint) │
└────────────────────────┬────────────────────────────────────┘
 │ if passed
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 5: DEPLOYMENT │
│ ├─ Deploy to Staging │
│ ├─ DAST - Dynamic Application Security Testing │
│ │ └─ OWASP ZAP │
│ ├─ Smoke Tests │
│ └─ Security Validation Tests │
└────────────────────────┬────────────────────────────────────┘
 │ manual approval for prod
┌────────────────────────▼────────────────────────────────────┐
│ PHASE 6: PRODUCTION │
│ ├─ Blue/Green Deployment │
│ ├─ Runtime Security Monitoring │
│ ├─ Continuous Compliance Scanning │
│ └─ Security Event Monitoring │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration des Outils de Sécurité

### 1. SAST - CodeQL (GitHub Advanced Security)

**Fichier:** `.github/workflows/codeql.yml`

```yaml
name: "CodeQL Security Scan"

on:
 push:
 branches: [ main, develop ]
 pull_request:
 branches: [ main, develop ]
 schedule:
 - cron: '0 6 * * 1' # Lundi 6h UTC

jobs:
 analyze:
 name: Analyze
 runs-on: ubuntu-latest
 permissions:
 security-events: write
 actions: read
 contents: read

 strategy:
 fail-fast: false
 matrix:
 language: [ 'javascript', 'python' ]

 steps:
 - name: Checkout repository
 uses: actions/checkout@v4

 - name: Initialize CodeQL
 uses: github/codeql-action/init@v3
 with:
 languages: ${{ matrix.language }}
 queries: +security-extended,security-and-quality

 - name: Autobuild
 uses: github/codeql-action/autobuild@v3

 - name: Perform CodeQL Analysis
 uses: github/codeql-action/analyze@v3
 with:
 category: "/language:${{ matrix.language }}"

 - name: Upload SARIF
 uses: github/codeql-action/upload-sarif@v3
 if: always()
```

**Règles personnalisées:**
- Détection de secrets hardcodés
- Validation des entrées utilisateur
- Protection contre injection SQL
- Protection contre XSS
- Utilisation d'APIs crypto sécurisées

### 2. Secrets Scanning - Gitleaks

**Fichier:** `.github/workflows/secrets-scan.yml`

```yaml
name: "Secrets Scanning"

on:
 push:
 pull_request:

jobs:
 gitleaks:
 name: Gitleaks Scan
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4
 with:
 fetch-depth: 0 # Full history for comprehensive scan

 - name: Run Gitleaks
 uses: gitleaks/gitleaks-action@v2
 env:
 GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
 GITLEAKS_ENABLE_SUMMARY: true
```

**Configuration:** `.gitleaks.toml`

```toml
[extend]
useDefault = true

[[rules]]
id = "cyberide-api-key"
description = "CyberIDE API Key"
regex = '''(?i)cyberide[_-]?api[_-]?key['\"]?\s*[:=]\s*['"]?[a-zA-Z0-9]{32,}['"]?'''
tags = ["key", "cyberide"]

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)api[_-]?key['\"]?\s*[:=]\s*['"]?[a-zA-Z0-9]{20,}['"]?'''
tags = ["key", "API"]

[allowlist]
paths = [
 '''^\.env\.example$''',
 '''^README\.md$''',
 '''^docs/''',
]
```

**Pre-commit hook:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Gitleaks pre-commit hook

echo "Running Gitleaks scan..."
gitleaks protect --staged --verbose

if [ $? -eq 1 ]; then
 echo " Gitleaks detected secrets!"
 echo "Please remove secrets before committing."
 echo "If this is a false positive, add to .gitleaks.toml allowlist."
 exit 1
fi

echo " No secrets detected"
exit 0
```

### 3. Dependency Scanning

**Fichier:** `.github/workflows/dependency-scan.yml`

```yaml
name: "Dependency Security Scan"

on:
 push:
 branches: [ main, develop ]
 pull_request:
 schedule:
 - cron: '0 0 * * *' # Daily at midnight UTC

jobs:
 npm-audit:
 name: NPM Audit
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: Setup Node.js
 uses: actions/setup-node@v4
 with:
 node-version: '20'
 cache: 'npm'

 - name: Install dependencies
 run: npm ci

 - name: Run npm audit
 run: npm audit --audit-level=moderate
 continue-on-error: false

 - name: Check for outdated packages
 run: npm outdated || true

 pip-audit:
 name: Python Pip Audit
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: Setup Python
 uses: actions/setup-python@v5
 with:
 python-version: '3.10'

 - name: Install pip-audit
 run: pip install pip-audit

 - name: Run pip-audit
 run: pip-audit -r requirements.txt

 snyk:
 name: Snyk Security Scan
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: Run Snyk to check for vulnerabilities
 uses: snyk/actions/node@master
 env:
 SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
 with:
 args: --severity-threshold=high
```

### 4. Container Security Scanning

**Fichier:** `.github/workflows/container-scan.yml`

```yaml
name: "Container Security Scan"

on:
 push:
 branches: [ main, develop ]
 pull_request:

jobs:
 trivy:
 name: Trivy Scan
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: Build Docker images
 run: |
 docker-compose build

 - name: Run Trivy vulnerability scanner - Frontend
 uses: aquasecurity/trivy-action@master
 with:
 image-ref: 'cyberide-frontend:latest'
 format: 'sarif'
 output: 'trivy-frontend.sarif'
 severity: 'CRITICAL,HIGH'

 - name: Run Trivy vulnerability scanner - Backend
 uses: aquasecurity/trivy-action@master
 with:
 image-ref: 'cyberide-backend:latest'
 format: 'sarif'
 output: 'trivy-backend.sarif'
 severity: 'CRITICAL,HIGH'

 - name: Upload Trivy results to GitHub Security
 uses: github/codeql-action/upload-sarif@v3
 with:
 sarif_file: '.'
```

### 5. DAST - Dynamic Application Security Testing

**Fichier:** `.github/workflows/dast.yml`

```yaml
name: "DAST - OWASP ZAP Scan"

on:
 push:
 branches: [ main, develop ]
 schedule:
 - cron: '0 2 * * 1' # Weekly on Monday at 2 AM UTC

jobs:
 zap_scan:
 name: OWASP ZAP Scan
 runs-on: ubuntu-latest
 
 steps:
 - name: Checkout code
 uses: actions/checkout@v4

 - name: Start application
 run: |
 docker-compose up -d
 sleep 30 # Wait for services to be ready

 - name: ZAP Baseline Scan
 uses: zaproxy/action-baseline@v0.12.0 # Pinned version for reproducibility
 with:
 target: 'http://localhost:5173'
 rules_file_name: '.zap/rules.tsv'
 cmd_options: '-a'

 - name: ZAP Full Scan
 uses: zaproxy/action-full-scan@v0.10.0 # Pinned version for reproducibility
 with:
 target: 'http://localhost:5173'
 rules_file_name: '.zap/rules.tsv'
 cmd_options: '-a'

 - name: Stop application
 if: always()
 run: docker-compose down
```

**Configuration ZAP:** `.zap/rules.tsv`

```tsv
10010	IGNORE	(Cookie Set Without HttpOnly Flag)
10011	IGNORE	(Cookie Without Secure Flag in Dev)
10015	WARN	(Incomplete or No Cache-control)
```

---

## Politiques de Sécurité CI/CD

### Règles de Blocage (Build Fail)

Le build DOIT échouer si:

1. **SAST détecte:**
 - Vulnérabilité CRITICAL ou HIGH
 - Secrets hardcodés
 - Injection SQL possible
 - XSS non atténué

2. **SCA détecte:**
 - Dépendance avec vulnérabilité CRITICAL
 - Dépendance avec vulnérabilité HIGH non corrigée depuis >7 jours

3. **Secrets Scanning détecte:**
 - N'importe quel secret (aucune tolérance)

4. **Linting:**
 - Erreurs ESLint (warnings OK)
 - Erreurs TypeScript
 - Erreurs Ruff critiques
 - Erreurs mypy

5. **Tests:**
 - Coverage < 80%
 - Tests unitaires échoués
 - Tests de sécurité échoués

### Règles de Warning (Build Continue)

Génère un warning mais ne bloque pas:

1. **SCA:**
 - Vulnérabilité MEDIUM
 - Vulnérabilité LOW

2. **DAST:**
 - Findings MEDIUM (sauf CSRF, XSS, SQLi)
 - Findings LOW

3. **Container Scan:**
 - Vulnérabilité MEDIUM dans dépendances non critiques

### Exceptions et Waivers

Pour obtenir une exception temporaire:

1. **Créer un ticket** détaillant:
 - Nature de la vulnérabilité
 - Pourquoi elle ne peut pas être corrigée immédiatement
 - Plan de mitigation temporaire
 - Date de correction prévue

2. **Approbation requise:**
 - Security Lead (obligatoire)
 - CTO (pour CRITICAL)

3. **Durée maximum:**
 - CRITICAL: 7 jours
 - HIGH: 30 jours
 - MEDIUM: 90 jours

4. **Configuration de l'exception:**

```yaml
# .github/security-exceptions.yml
exceptions:
 - id: "CVE-2024-12345"
 severity: "HIGH"
 component: "example-lib@1.2.3"
 reason: "No patch available, mitigation in place"
 approved_by: "security-lead@iangelai.com"
 expires: "2024-12-31"
 mitigation: "Input validation added in wrapper"
```

---

## Métriques et Reporting

### Métriques Clés (KPIs)

1. **Mean Time to Detect (MTTD)**
 - Temps moyen entre introduction et détection d'une vulnérabilité
 - Objectif: < 1 jour

2. **Mean Time to Remediate (MTTR)**
 - Temps moyen entre détection et correction
 - Objectif:
 - CRITICAL: < 24h
 - HIGH: < 7 jours
 - MEDIUM: < 30 jours

3. **Vulnerability Density**
 - Nombre de vulnérabilités par 1000 lignes de code
 - Objectif: < 0.5

4. **False Positive Rate**
 - % de findings qui sont des faux positifs
 - Objectif: < 10%

5. **Security Test Coverage**
 - % du code couvert par des tests de sécurité
 - Objectif: > 80%

### Dashboard de Sécurité

```yaml
# Exemple de dashboard (Grafana / DataDog)
panels:
 - title: "Vulnérabilités par Sévérité"
 type: "pie"
 metrics:
 - critical: count
 - high: count
 - medium: count
 - low: count

 - title: "MTTR par Sévérité"
 type: "bar"
 metrics:
 - critical: avg(time_to_remediate)
 - high: avg(time_to_remediate)
 - medium: avg(time_to_remediate)

 - title: "Scans Réussis vs Échoués"
 type: "line"
 metrics:
 - passed: count(status=passed)
 - failed: count(status=failed)

 - title: "Top 10 Vulnérabilités"
 type: "table"
 columns: [CVE, Severity, Component, Status, Age]
```

---

## Best Practices DevSecOps

### 1. Automatisation Maximale

- Tous les scans automatisés dans CI/CD
- Pas de scans manuels sauf audit externe
- Notifications automatiques (Slack, Email)
- Tickets automatiques pour vulnérabilités

### 2. Feedback Rapide

- Résultats en < 10 minutes pour PR
- Notifications immédiates si échec
- Liens directs vers les findings
- Suggestions de correction automatiques

### 3. Shift Left

- Pre-commit hooks actifs
- IDE plugins de sécurité
- Formation continue des devs
- Security champions dans chaque équipe

### 4. Culture de Sécurité

- Sécurité = responsabilité partagée
- Pas de blâme pour introduction de vulnérabilités
- Célébrer les corrections rapides
- Partage des learnings

### 5. Amélioration Continue

- Révision mensuelle des métriques
- Post-mortems après incidents
- Mise à jour régulière des outils
- Veille sur nouvelles menaces

---

## 📞 Support et Ressources

### Contacts

- **DevSecOps Lead:** devsecops@iangelai.com
- **Security Team:** security@iangelai.com
- **On-call Security:** security-oncall@iangelai.com

### Documentation Complémentaire

- [SECURITY.md](../../SECURITY.md) - Politique de sécurité globale
- [secrets_management_guide.md](./secrets_management_guide.md) - Gestion des secrets
- [incident_response_guide.md](./incident_response_guide.md) - Réponse aux incidents

### Outils et Ressources

- **GitHub Advanced Security:** https://docs.github.com/en/code-security
- **OWASP DevSecOps:** https://owasp.org/www-project-devsecops-guideline/
- **NIST DevSecOps:** https://csrc.nist.gov/projects/devsecops

---

<div align="center">

** Automatiser, Détecter, Corriger, Répéter **

*"Security is not a phase, it's a continuous process."*

</div>
