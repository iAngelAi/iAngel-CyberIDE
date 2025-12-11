# ADR-001: Infrastructure de Logging pour CyberIDE Neural Core

## Statut

**Approuvé** — 2025-12-05

## Contexte

Le backend Python `neural_cli/` du projet CyberIDE utilise actuellement **62+ appels `print()`** pour tous les messages : démarrage, connexions WebSocket, erreurs, diagnostics. Cette approche pose plusieurs problèmes :

1. **Aucune catégorisation** : Impossible de filtrer par sévérité (INFO vs WARNING vs ERROR)
2. **Tests silencieux** : Les messages ne sont pas capturables par pytest sans `capsys`
3. **Production inadéquate** : Pas de rotation de logs, pas de format structuré
4. **Validators muets** : Les validators Pydantic (`BrainRegion.coverage`, `NeuralStatus.illumination`, `ProjectMetrics`) clampent silencieusement les valeurs hors bornes sans avertir le développeur

### Cas Problématique : Validators Pydantic

```python
# models.py - Comportement actuel (silencieux)
@field_validator('coverage')
@classmethod
def validate_coverage(cls, v: float) -> float:
    return max(0.0, min(100.0, v))  # Clamping silencieux!
```

Si un appelant passe `coverage=150.0`, la valeur est clampée à `100.0` sans aucun signal.

### Inventaire des Messages Actuels

| Catégorie | Emoji | Quantité | Exemple |
|-----------|-------|----------|---------|
| Succès | `✓` | 15 | `✓ Neural Core Online` |
| Information | `ℹ` | 12 | `ℹ Starting file watcher...` |
| Warning | `⚠` | 10 | `⚠ Tests already running` |
| Erreur | `❌` | 8 | `❌ Failed to save status` |
| Thématique | `🧠🎯🌊` | 17 | `🧠 CyberIDE NEURAL CORE` |

---

## Décision

Adopter une approche **hybride pragmatique** basée sur le module `logging` standard de Python.

### Choix Techniques

| Aspect | Décision | Justification |
|--------|----------|---------------|
| Bibliothèque | `logging` standard | Pas de dépendance externe, suffisant pour le besoin |
| Validators | `logging.warning()` | Sémantiquement correct pour "valeur corrigée" |
| Format | Texte lisible | Projet personnel, debugging en terminal |
| Loggers | Un par module (`__name__`) | Filtrage granulaire possible |
| Emojis | Conservés | Identité visuelle Neural Core |

### Pourquoi pas `warnings.warn()` ?

| Critère | `logging.warning()` | `warnings.warn()` |
|---------|---------------------|-------------------|
| Capture pytest | Via `caplog` fixture | Via `recwarn` |
| Sémantique | "Situation anormale" | "Dépréciation API" |
| Centralisation | Un seul système | Deux systèmes parallèles |

`warnings.warn()` est conçu pour les **dépréciations**, pas pour des valeurs corrigées automatiquement.

### Pourquoi pas `structlog` ?

Sur-ingénierie pour un projet personnel sans infrastructure de log aggregation (ELK, Datadog).

---

## Conséquences

### Positives

1. **Filtrage par sévérité** : `NEURAL_LOG_LEVEL=WARNING` en production
2. **Capture pytest** : Via `caplog` fixture sans modification du code
3. **Traçabilité** : Timestamp et module source automatiques
4. **Évolutivité** : Ajout de handlers (fichier, JSON) sans modifier le code métier

### Négatives

1. **Migration initiale** : 62+ `print()` à remplacer progressivement
2. **Configuration** : Nécessite un point d'entrée pour `setup_logging()`

---

## Spécification Technique

### Configuration Logging

Fichier : `neural_cli/logging_config.py`

```python
"""Logging configuration for CyberIDE Neural Core."""

import logging
import os
import sys
from typing import Final

LOG_FORMAT: Final[str] = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"


def setup_logging() -> None:
    """Configure logging at application startup."""
    log_level_name = os.getenv("NEURAL_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Reduce third-party noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchdog").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)
```

### Pattern Validator avec Warning

```python
import logging
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class BrainRegion(BaseModel):
    coverage: float = Field(default=0.0)  # Pas de ge/le — le validator gère

    @field_validator('coverage')
    @classmethod
    def validate_coverage(cls, v: float) -> float:
        if v < 0.0:
            logger.warning(
                "BrainRegion.coverage=%.2f below 0.0, clamping. "
                "Check upstream calculation.", v
            )
            return 0.0
        if v > 100.0:
            logger.warning(
                "BrainRegion.coverage=%.2f exceeds 100.0, clamping. "
                "Check upstream calculation.", v
            )
            return 100.0
        return v
```

### Pattern Migration print()

```python
# Avant
print(f"⚠ Error sending to client: {e}")

# Après (lazy formatting)
logger.warning("⚠ Error sending to client: %s", e)
```

### Configuration pytest

```toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "WARNING"
log_cli_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
```

---

## Plan d'Implémentation

| Phase | Tâche | Priorité |
|-------|-------|----------|
| 1 | Créer `logging_config.py` | Critique |
| 2 | Corriger validators `models.py` | Haute |
| 3 | Migrer `main.py` print() | Haute |
| 4 | Migrer autres modules | Moyenne |

---

## Métriques de Succès

| Métrique | Avant | Cible |
|----------|-------|-------|
| `print()` dans neural_cli/ | 62+ | 0 |
| Warnings validators | 0 | 100% des validators qui clampent |
| Tests caplog | 0 | Couverture des cas de warning |

---

## Références

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [pytest logging documentation](https://docs.pytest.org/en/latest/how-to/logging.html)

---

## Historique

| Date | Action | Auteur |
|------|--------|--------|
| 2025-12-05 | Création et approbation | @architecte-principal / Fil |
