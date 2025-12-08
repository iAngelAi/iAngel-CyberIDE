# 🔐 Guide de Gestion des Secrets — CyberIDE

<div align="center">

**Version 1.0.0** | Décembre 2024

*"Never commit secrets. Ever."*

</div>

---

## 📋 Vue d'Ensemble

Les secrets (clés API, mots de passe, tokens, certificats) sont des cibles de choix pour les attaquants. Une fuite de secret peut compromettre l'ensemble du système.

**Règle d'or:** ❌ Aucun secret ne doit JAMAIS être commité dans le code source.

---

## 🎯 Types de Secrets

### Classification

| Type | Exemples | Risque | Protection |
|------|----------|--------|------------|
| **API Keys** | OpenAI, Stripe, AWS | HIGH | Rotation fréquente, scope limité |
| **Database Credentials** | PostgreSQL, MongoDB | CRITICAL | Chiffrement, accès restreint |
| **Private Keys** | SSH, TLS/SSL | CRITICAL | Hardware security module (HSM) |
| **Tokens** | JWT, OAuth | HIGH | Courte durée de vie, révocation |
| **Certificates** | mTLS, Code signing | HIGH | Stockage sécurisé, rotation |
| **Encryption Keys** | AES, RSA | CRITICAL | Key management service (KMS) |

---

## ✅ Bonnes Pratiques

### 1. Variables d'Environnement

```bash
# ✅ .env (NON versionné, dans .gitignore)
DATABASE_URL=postgresql://user:password@localhost:5432/cyberide
API_KEY=sk-1234567890abcdef
JWT_SECRET=super-secret-key-change-me

# ✅ .env.example (versionné, valeurs exemples)
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
API_KEY=your-api-key-here
JWT_SECRET=generate-secure-random-string
```

**`.gitignore`:**
```gitignore
# Secrets
.env
.env.local
.env.*.local
*.key
*.pem
*.pfx
secrets/
```

### 2. Accès aux Secrets dans le Code

#### TypeScript (Frontend/Node.js)

```typescript
// ✅ REQUIS - Variables d'environnement avec validation
import { z } from 'zod';

const EnvSchema = z.object({
  VITE_API_KEY: z.string().min(32, 'API key must be at least 32 characters'),
  VITE_API_URL: z.string().url('Must be a valid URL'),
});

// Valider au démarrage
const env = EnvSchema.parse(import.meta.env);

// Utiliser de manière sécurisée
async function callAPI() {
  const response = await fetch(env.VITE_API_URL, {
    headers: {
      'Authorization': `Bearer ${env.VITE_API_KEY}`,
    },
  });
  return response.json();
}
```

#### Python (Backend)

```python
# ✅ REQUIS - Pydantic Settings
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    database_url: str = Field(..., min_length=10)
    api_key: str = Field(..., min_length=32)
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(('postgresql://', 'postgres://')):
            raise ValueError('Database URL must start with postgresql://')
        return v
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v.startswith('sk-'):
            raise ValueError('API key must start with sk-')
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()
```

### 3. Rotation des Secrets

```python
# ✅ Support de multiple secrets pour rotation sans downtime
class RotatingSecrets(BaseSettings):
    # Secrets actifs (nouvellement générés)
    jwt_secret_primary: str
    api_key_primary: str
    
    # Secrets en phase de déprécia tion (encore acceptés)
    jwt_secret_secondary: str | None = None
    api_key_secondary: str | None = None
    
    def validate_jwt(self, token: str) -> dict:
        """Try primary first, fallback to secondary."""
        try:
            return jwt.decode(token, self.jwt_secret_primary, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            if self.jwt_secret_secondary:
                return jwt.decode(token, self.jwt_secret_secondary, algorithms=["HS256"])
            raise

secrets = RotatingSecrets()
```

**Processus de rotation:**
1. Générer nouveau secret (devient "primary")
2. Ancien secret devient "secondary"
3. Grace period: 24-48h (les deux sont acceptés)
4. Supprimer secondary après grace period

### 4. Masquage dans les Logs

```python
import structlog
import re

def mask_sensitive_data(data: dict) -> dict:
    """Mask sensitive data in logs."""
    masked = data.copy()
    
    # Patterns sensibles
    sensitive_patterns = {
        'api_key': r'(sk-|pk-|token-)[a-zA-Z0-9]+',
        'jwt': r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'password': r'password',
    }
    
    for key, value in masked.items():
        if isinstance(value, str):
            for pattern_name, pattern in sensitive_patterns.items():
                if re.search(pattern, value, re.IGNORECASE):
                    masked[key] = "***REDACTED***"
                    break
    
    return masked

logger = structlog.get_logger()

# ✅ Usage
logger.info("api_call", **mask_sensitive_data({
    "endpoint": "/api/users",
    "api_key": "sk-1234567890abcdef",  # Sera masqué
    "user_id": "123",  # OK
}))
```

---

## 🔒 Gestion des Secrets en Production

### GitHub Secrets (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy application
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        API_KEY: ${{ secrets.API_KEY }}
        JWT_SECRET: ${{ secrets.JWT_SECRET }}
      run: |
        # Les secrets ne sont JAMAIS loggés
        echo "Deploying..."
        # Utiliser les variables d'environnement
```

**Configuration dans GitHub:**
1. Repository → Settings → Secrets and variables → Actions
2. New repository secret
3. Nom: `DATABASE_URL`, `API_KEY`, etc.
4. Valeur: Le secret (jamais affiché après sauvegarde)

### Vault / Secrets Manager

Pour production, utiliser un gestionnaire de secrets dédié:

#### HashiCorp Vault

```python
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')

# Lecture d'un secret
secret = client.secrets.kv.v2.read_secret_version(
    path='cyberide/production/database'
)
database_url = secret['data']['data']['url']
```

#### AWS Secrets Manager

```python
import boto3
import json

client = boto3.client('secretsmanager', region_name='us-east-1')

response = client.get_secret_value(SecretId='cyberide/production/api-keys')
secrets = json.loads(response['SecretString'])

api_key = secrets['api_key']
```

#### Azure Key Vault

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://cyberide-vault.vault.azure.net", credential=credential)

api_key = client.get_secret("api-key").value
```

---

## 🔍 Détection de Secrets Exposés

### Gitleaks (Pre-commit + CI)

**Installation:**
```bash
# macOS
brew install gitleaks

# Linux
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/
```

**Pre-commit hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Scanning for secrets with Gitleaks..."

gitleaks protect --staged --verbose

if [ $? -eq 1 ]; then
  echo ""
  echo "❌ ERROR: Gitleaks detected secrets in your staged files!"
  echo ""
  echo "🚨 NEVER commit secrets to git!"
  echo ""
  echo "If this is a false positive:"
  echo "  1. Add to .gitleaks.toml allowlist"
  echo "  2. Re-stage and commit"
  echo ""
  exit 1
fi

echo "✅ No secrets detected"
exit 0
```

### TruffleHog

```bash
# Scan tout l'historique
trufflehog git file://. --json

# Scan depuis un commit spécifique
trufflehog git file://. --since-commit HEAD~10

# Scan avec filtres
trufflehog git file://. \
  --exclude-paths .trufflehog-exclude \
  --json \
  --only-verified
```

### git-secrets (AWS)

```bash
# Installation
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
sudo make install

# Configuration
cd /path/to/repo
git secrets --install
git secrets --register-aws

# Scan
git secrets --scan
git secrets --scan-history
```

---

## 🚨 Que Faire si un Secret est Exposé?

### Processus de Réponse Immédiate

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: DÉTECTION (0-5 min)                           │
│ ├─ Secret détecté dans commit/PR                       │
│ ├─ Alerte automatique (Gitleaks/GitHub)                │
│ └─ Notification Security Team                          │
├─────────────────────────────────────────────────────────┤
│ PHASE 2: ÉVALUATION (5-15 min)                         │
│ ├─ Identifier le type de secret                        │
│ ├─ Évaluer l'exposition (public/privé repo)            │
│ ├─ Déterminer la criticité                             │
│ └─ Vérifier si secret est actif                        │
├─────────────────────────────────────────────────────────┤
│ PHASE 3: CONFINEMENT (15-30 min)                       │
│ ├─ RÉVOQUER le secret immédiatement                    │
│ ├─ Bloquer l'accès avec ce secret                      │
│ ├─ Vérifier les logs d'utilisation                     │
│ └─ Identifier les accès suspects                       │
├─────────────────────────────────────────────────────────┤
│ PHASE 4: ÉRADICATION (30 min - 2h)                     │
│ ├─ Générer nouveau secret                              │
│ ├─ Mettre à jour partout où nécessaire                 │
│ ├─ Nettoyer l'historique git (si nécessaire)           │
│ └─ Valider que ancien secret est révoqué               │
├─────────────────────────────────────────────────────────┤
│ PHASE 5: POST-MORTEM (< 24h)                           │
│ ├─ Documenter l'incident                               │
│ ├─ Identifier la cause racine                          │
│ ├─ Mettre en place préventions                         │
│ └─ Former l'équipe                                     │
└─────────────────────────────────────────────────────────┘
```

### Nettoyage de l'Historique Git

**⚠️ ATTENTION:** Réécrit l'historique, nécessite force push!

```bash
# Option 1: BFG Repo-Cleaner (recommandé)
java -jar bfg.jar --replace-text secrets.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# Option 2: git-filter-repo
git filter-repo --invert-paths --path secrets.env

# Option 3: git filter-branch (legacy)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
```

### Révocation par Type

#### API Keys

```python
# Immediate revocation via API
import requests

response = requests.delete(
    'https://api.service.com/v1/keys/sk-1234567890',
    headers={'Authorization': f'Bearer {admin_token}'}
)

# Generate new key
new_key = requests.post(
    'https://api.service.com/v1/keys',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'name': 'cyberide-production'}
).json()['key']
```

#### Database Credentials

```sql
-- PostgreSQL
ALTER USER cyberide_app WITH PASSWORD 'new-secure-password';

-- Revoke sessions actives
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE usename = 'cyberide_app' 
  AND pid <> pg_backend_pid();
```

#### JWT Secrets

```python
# 1. Changer JWT_SECRET
# 2. Invalider tous les tokens existants
redis_client.flushdb()  # Si cache de tokens

# 3. Forcer re-authentication
# Tous les utilisateurs devront se reconnecter
```

---

## 📋 Checklist de Sécurité des Secrets

### Développement Local

- [ ] `.env` dans `.gitignore`
- [ ] `.env.example` avec valeurs exemples
- [ ] Pre-commit hook Gitleaks actif
- [ ] IDE plugin pour détection de secrets
- [ ] Pas de secrets hardcodés dans le code

### CI/CD

- [ ] GitHub Secrets configurés
- [ ] Secrets scanning actif (Gitleaks)
- [ ] Secrets rotation automatique
- [ ] Logs masqués (pas d'exposition de secrets)
- [ ] Environnements séparés (dev/staging/prod)

### Production

- [ ] Vault/Secrets Manager utilisé
- [ ] Rotation automatique activée
- [ ] Monitoring d'accès aux secrets
- [ ] Alertes sur anomalies
- [ ] Backups chiffrés

### Conformité

- [ ] Politique de gestion des secrets documentée
- [ ] Formation de l'équipe effectuée
- [ ] Audit régulier des secrets
- [ ] Plan de réponse aux incidents
- [ ] Registre des secrets maintenu

---

## 🎓 Formation et Sensibilisation

### Quiz pour l'Équipe

1. **Où NE DOIT-ON JAMAIS mettre un secret?**
   - [ ] Dans le code source
   - [ ] Dans un commit git
   - [ ] Dans un message Slack
   - [ ] Dans un fichier README
   - [x] Tous les choix ci-dessus

2. **Comment stocker un secret en production?**
   - [ ] Dans .env commité
   - [ ] Hardcodé dans le code
   - [x] Dans un secrets manager (Vault, AWS Secrets Manager)
   - [ ] Dans les variables d'environnement du système

3. **Que faire si on découvre un secret exposé?**
   - [x] Le révoquer immédiatement
   - [ ] L'ignorer si le repo est privé
   - [ ] Le supprimer du dernier commit seulement
   - [ ] Attendre la prochaine rotation

### Exercices Pratiques

1. **Scénario 1:** Un développeur a commité une API key
   - Simuler la détection avec Gitleaks
   - Pratiquer la révocation
   - Nettoyer l'historique

2. **Scénario 2:** Migration vers Vault
   - Setup Vault local (Docker)
   - Migrer secrets de .env vers Vault
   - Modifier app pour lire depuis Vault

3. **Scénario 3:** Rotation de secrets
   - Implémenter rotation sans downtime
   - Tester avec JWT secrets
   - Valider monitoring

---

## 📚 Ressources

### Outils

- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **TruffleHog:** https://github.com/trufflesecurity/trufflehog
- **git-secrets:** https://github.com/awslabs/git-secrets
- **HashiCorp Vault:** https://www.vaultproject.io/
- **AWS Secrets Manager:** https://aws.amazon.com/secrets-manager/
- **Azure Key Vault:** https://azure.microsoft.com/en-us/services/key-vault/

### Guides

- **OWASP Secrets Management:** https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- **GitHub Secret Scanning:** https://docs.github.com/en/code-security/secret-scanning
- **NIST SP 800-57:** Key Management Guidelines

---

<div align="center">

**🔐 Zero Secrets in Code. Always. 🔐**

*"The best secret is one that doesn't exist in your repository."*

</div>
