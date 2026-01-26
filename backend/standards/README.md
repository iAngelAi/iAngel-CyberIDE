# Standards Python — Règles Fil

Ce dossier contient les standards de code Python stricts pour le projet CyberIDE.

## Configuration Ruff (`pyproject.strict.toml`)

### Version cible
- **Python 3.11** — Utilisation des fonctionnalités modernes du langage

### Longueur de ligne
- **88 caractères** — Standard Black/Ruff pour une lisibilité optimale

### Règles de lint activées

| Code | Catégorie | Description |
|------|-----------|-------------|
| `E` | pycodestyle errors | Erreurs de style PEP 8 |
| `W` | pycodestyle warnings | Avertissements de style PEP 8 |
| `F` | Pyflakes | Détection d'erreurs logiques |
| `I` | isort | Tri et organisation des imports |
| `B` | flake8-bugbear | Bugs probables et anti-patterns |
| `C4` | flake8-comprehensions | Optimisation des compréhensions |
| `UP` | pyupgrade | Modernisation de la syntaxe Python |
| `ARG` | flake8-unused-arguments | Arguments non utilisés |
| `SIM` | flake8-simplify | Simplification du code |
| `TCH` | flake8-type-checking | Imports pour type checking |
| `DTZ` | flake8-datetimez | Gestion correcte des timezones |
| `ERA` | eradicate | Détection de code commenté |
| `PTH` | flake8-use-pathlib | Utilisation de pathlib vs os.path |
| `RUF` | Ruff-specific | Règles spécifiques à Ruff |
| `ANN` | flake8-annotations | Annotations de type obligatoires |
| `ASYNC` | flake8-async | Bonnes pratiques async/await |
| `S` | flake8-bandit | Vulnérabilités de sécurité |
| `BLE` | flake8-blind-except | Éviter les except génériques |

### Règles ignorées

| Code | Raison |
|------|--------|
| `E501` | Longueur de ligne gérée par le formatter |
| `S101` | Assertions autorisées (tests) |
| `ANN101` | `self` n'a pas besoin d'annotation |
| `ANN102` | `cls` n'a pas besoin d'annotation |
| `ANN401` | `Any` dynamique parfois nécessaire |

## Configuration MyPy

### Mode strict activé
- **`strict = true`** — Toutes les vérifications strictes
- **`disallow_any_explicit = true`** — Interdiction de `Any` explicite

## Utilisation

Pour appliquer ces standards à votre projet, copiez la configuration dans votre `pyproject.toml` racine :

```bash
# Vérifier le code
ruff check .

# Corriger automatiquement
ruff check --fix .

# Vérifier les types
mypy .
```

## Philosophie Fil

> **"Le code doit être correct par construction, pas par convention."**

Ces règles strictes garantissent :
1. **Sécurité de type** — Détection des erreurs à l'écriture
2. **Maintenabilité** — Code lisible et cohérent
3. **Performance** — Patterns optimaux encouragés
4. **Sécurité** — Vulnérabilités détectées automatiquement
