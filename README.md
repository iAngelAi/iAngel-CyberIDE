# 🧠 CyberIDE — Neural Architect

<div align="center">

![CyberIDE Banner](https://img.shields.io/badge/CyberIDE-Neural%20Architect-00ffff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6Ii8+PC9zdmc+)

**Un environnement de développement avec visualisation 3D d'un cerveau neural qui reflète la santé de votre projet en temps réel.**

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-black?logo=three.js)](https://docs.pmnd.rs/react-three-fiber/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://python.org/)

</div>

---

## 🎯 Concept

CyberIDE visualise la **santé de votre code** sous forme d'un cerveau neural 3D. Les voies neurales s'illuminent progressivement selon :

- ✅ Les tests qui passent
- 📚 La documentation présente
- 🔒 La sécurité du code
- 🏗️ L'architecture des modules

### Métaphore Visuelle (Neural Illumination)

| Niveau | Critères | Effet Visuel |
|--------|----------|--------------|
| 0% | Projet vide | Noir complet |
| 25% | Structure de base + config | Faible lueur bleue (tronc cérébral) |
| 50% | Logique métier + modules | Lobes illuminés, connexions lentes |
| 75% | Tests passés + docs | Pulsations rapides, cyan/magenta |
| 100% | Prod ready + sécurité | **FULL UPLINK** (blanc/or éclatant) |
| ERROR | Test failed / régression | 🔴 **ZONE ROUGE** + diagnostic |

---

## 🚀 Démarrage Rapide

### Prérequis

- Node.js 18+
- Python 3.8+
- npm ou pnpm

### Installation

```bash
# Cloner le projet
git clone https://github.com/iAngelAi/iAngel-CyberIDE.git
cd iAngel-CyberIDE

# Installer les dépendances frontend
npm install

# Installer les dépendances backend
pip install -r requirements.txt
```

### Lancement

```bash
# Option 1: Tout-en-un (recommandé)
python3 neural_core.py

# Option 2: Séparé
# Terminal 1 - Frontend (port 5173)
npm run dev

# Terminal 2 - Backend (port 8000)
python3 neural_core.py --backend
```

Ouvrez http://localhost:5173 pour voir le cerveau neural.

---

## 🏗️ Architecture

```
CyberIDE/
├── src/                          # Frontend React + Three.js
│   ├── components/
│   │   ├── Brain3D/              # Visualisation 3D du cerveau
│   │   ├── DNAHelix/             # Animation ADN
│   │   ├── Diagnostics/          # Overlays d'erreurs
│   │   └── GitDashboard/         # Dashboard Git
│   ├── hooks/
│   │   ├── useBrainState.ts      # État du cerveau
│   │   └── useWebSocket.ts       # Connexion temps réel
│   ├── schemas/
│   │   └── websocketValidation.ts # Validation Zod
│   └── types/                    # Types TypeScript
│
├── neural_cli/                   # Backend Python FastAPI
│   ├── main.py                   # Serveur FastAPI + WebSocket
│   ├── models.py                 # Modèles Pydantic
│   ├── file_watcher.py           # Surveillance fichiers (watchdog)
│   ├── test_analyzer.py          # Intégration pytest
│   ├── metric_calculator.py      # Calcul d'illumination
│   └── git_pulse.py              # Analyse commits Git
│
├── tests/                        # Tests Python (pytest)
├── src/__tests__/                # Tests Frontend (Vitest)
│
├── neural_core.py                # Script de lancement universel
└── CLAUDE.md                     # Instructions pour Claude Code
```

### Flux de Communication

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Frontend      │◄──────────────────►│    Backend      │
│   React + R3F   │   ws://8000/ws     │   FastAPI       │
│   (port 5173)   │                    │   (port 8000)   │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ Render 3D                            │ Watch Files
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│   Three.js      │                    │   watchdog      │
│   Brain Scene   │                    │   pytest        │
└─────────────────┘                    └─────────────────┘
```

---

## 🛠️ Stack Technique

### Frontend

| Technologie | Usage |
|-------------|-------|
| **React 19** | Framework UI |
| **Three.js / R3F** | Rendu 3D du cerveau |
| **Tailwind CSS** | Styling (palette cyberpunk) |
| **TypeScript** | Typage strict |
| **Zod** | Validation runtime |
| **Vitest** | Tests unitaires |

### Backend

| Technologie | Usage |
|-------------|-------|
| **FastAPI** | API REST + WebSocket |
| **uvicorn** | Serveur ASGI |
| **watchdog** | Surveillance fichiers |
| **pytest** | Analyse des tests |
| **Pydantic** | Modèles de données |

---

## 📋 Commandes Disponibles

### Frontend

```bash
npm run dev          # Serveur de développement (HMR)
npm run build        # Build production
npm run preview      # Prévisualiser le build
npm run lint         # ESLint
npm test             # Tests Vitest
npm run test:ui      # Interface Vitest
npm run test:coverage # Couverture de code
```

### Backend

```bash
python3 neural_core.py           # Frontend + Backend
python3 neural_core.py --backend # Backend seul
python3 neural_core.py --check   # Vérifier dépendances
python3 neural_core.py --init    # Initialiser structure

pytest                           # Tous les tests
pytest -v                        # Mode verbeux
pytest --cov=neural_cli tests/   # Avec couverture
```

---

## 🎨 Thème Cyberpunk

La palette de couleurs est définie dans `tailwind.config.js` :

| Couleur | Hex | Usage |
|---------|-----|-------|
| Cyan | `#00ffff` | Illumination principale |
| Magenta | `#ff00ff` | Accents, pulsations |
| Noir profond | `#0a0a0f` | Background |
| Blanc/Or | `#ffffd4` | Full Uplink (100%) |
| Rouge | `#ff0040` | Erreurs, Zone Rouge |

---

## 🧪 Tests

### Test-Driven Illumination

> **Règle fondamentale** : No test = No light

Chaque module doit avoir des tests associés. La couverture de tests influence directement l'illumination du cerveau neural.

```bash
# Frontend (Vitest)
npm test

# Backend (pytest)
pytest

# Couverture complète
npm run test:coverage
pytest --cov=neural_cli tests/
```

---

## 📁 Fichiers Clés

| Fichier | Description |
|---------|-------------|
| `neural_status.json` | État temps réel (généré automatiquement) |
| `neural_config.json` | Configuration du projet (le "soul") |
| `CLAUDE.md` | Instructions pour Claude Code |
| `.claude/CLAUDE.md` | Persona Neural Architect |

---

## 🔧 Configuration

### Variables d'Environnement

Copiez `.env.example` vers `.env` :

```bash
cp .env.example .env
```

```env
VITE_API_URL=http://localhost:8000
BACKEND_PORT=8000
FRONTEND_PORT=5173
NODE_ENV=development
```

---

## 🚫 Règles de Code Strictes

### TypeScript

```typescript
// ❌ INTERDIT - Cast "as"
const data = response as NeuralStatus;

// ✅ REQUIS - Validation Zod
const result = NeuralStatusSchema.safeParse(response);
if (!result.success) throw new ValidationError(result.error);
const data = result.data;
```

### Python

```python
# ✅ Type hints obligatoires
def calculate_illumination(metrics: MetricData) -> float:
    ...

# ✅ Pydantic pour les modèles
class NeuralStatus(BaseModel):
    illumination_level: float
    regions: list[BrainRegion]
```

---

## 🐳 Docker (Optionnel)

```bash
# Build et lancement
docker-compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

---

## 📚 Documentation Supplémentaire

- [QUICKSTART.md](./QUICKSTART.md) — Guide de démarrage rapide
- [NEURAL_CORE_GUIDE.md](./NEURAL_CORE_GUIDE.md) — Guide complet du Neural Core
- [SETUP.md](./SETUP.md) — Instructions d'installation détaillées
- [ROADMAP.md](./ROADMAP.md) — Feuille de route du projet

---

## 🤝 Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing-feature`)
3. Committez (`git commit -m 'feat: Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

### Convention de Commits

```
feat:     Nouvelle fonctionnalité
fix:      Correction de bug
docs:     Documentation
test:     Ajout de tests
refactor: Refactoring
style:    Formatage (pas de changement de code)
chore:    Maintenance
```

---

## 📄 Licence

Ce projet est sous licence propriétaire. Voir le fichier `LICENSE` pour plus de détails.

---

<div align="center">

**Développé avec 🧠 par [iAngelAi](https://github.com/iAngelAi)**

*"No test = No light. Let your code illuminate the neural pathways."*

</div>
