# CLAUDE.md

> **⚠️ HIÉRARCHIE DES INSTRUCTIONS**
>
> Ce fichier complète la configuration globale `~/.claude/CLAUDE.md`.
> En cas de conflit, les **règles globales prévalent**.
> Les **13 agents spécialisés** (`~/.claude/agents/`) s'appliquent à ce projet.
>
> **Claude agit comme CTO** et orchestre les agents selon les patterns définis globalement.
> 
> **Agent principal pour ce projet** : `@ingenieur-graphique-3d` (Three.js, WebGL, optimisation 60 FPS)
> **Agents secondaires** : `@developpeur-fullstack` (React/FastAPI), `@ingenieur-qa-automation` (tests)
>
> Voir `~/.claude/standards/tsconfig.strict.json` pour les standards TypeScript stricts.

---

## 🎯 Contexte du Projet CyberIDE

**Type** : Projet **PERSONNEL** (pas de contraintes Loi 25/PIPEDA)

**CyberIDE** est un environnement de développement avec visualisation 3D d'un cerveau neural
qui reflète la santé du projet. Les voies neurales s'illuminent progressivement selon les tests,
la documentation et les intégrations.

Ce projet utilise intensivement **Three.js/R3F** pour le rendu 3D, ce qui justifie l'utilisation
de `@ingenieur-graphique-3d` comme agent principal pour les questions de performance et de shaders.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 1.1.0
**Last Updated**: 2025-12-01
**Project**: CyberIDE — Neural Architect

---

## Vision du Projet

CyberIDE est un environnement de développement avec visualisation 3D d'un cerveau neural qui reflète la santé du projet. Les voies neurales s'illuminent progressivement selon les tests, la documentation et les intégrations.

### Métaphore Visuelle (Neural Illumination)

| Niveau | Critères | Effet Visuel |
|--------|----------|--------------|
| 0% | Projet vide | Noir complet |
| 25% | Structure de base + config | Faible lueur bleue (tronc cérébral) |
| 50% | Logique métier + modules | Lobes illuminés, connexions lentes |
| 75% | Tests passés + docs | Pulsations rapides, cyan/magenta |
| 100% | Prod ready + sécurité | FULL UPLINK (blanc/or éclatant) |
| ERROR | Test failed / régression | ZONE ROUGE + diagnostic |

---

## Development Commands

### Full System (Recommended)
```bash
# Start both frontend and backend
python3 neural_core.py

# Or with npm script
npm start
```

### Frontend Only
```bash
npm run dev              # Vite dev server (port 5173)
npm run build            # Production build
npm run lint             # ESLint
npm run preview          # Preview production build
```

### Frontend Tests (Vitest)
```bash
npm test                 # Run tests once
npm run test:watch       # Watch mode
npm run test:ui          # Vitest UI
npm run test:coverage    # With coverage
```

### Backend Only
```bash
python3 neural_core.py --backend    # FastAPI server (port 8000)

# Or directly with uvicorn
uvicorn neural_cli.main:app --reload --port 8000
```

### Python Tests
```bash
pytest                              # Run all tests
pytest tests/test_models.py         # Single file
pytest -v                           # Verbose
pytest --cov=neural_cli tests/      # With coverage
```

### System Check
```bash
python3 neural_core.py --check      # Verify all dependencies
python3 neural_core.py --init       # Initialize project structure
```

---

## Architecture

### Frontend (React + Three.js)
```
src/
  App.tsx                    # Main app, WebSocket handling, UI layout
  hooks/
    useBrainState.ts         # Brain visualization state management
    useWebSocket.ts          # WebSocket connection with auto-reconnect
  components/
    Brain3D/                 # Three.js 3D brain visualization
    Diagnostics/             # Error overlays
  types/
    backend.ts               # TypeScript types mirroring Python models
    index.ts                 # Frontend-specific types
  schemas/
    websocketValidation.ts   # Zod schemas for runtime validation
  utils/
    brainHelpers.ts          # Illumination calculations
  __tests__/                 # Vitest tests
```

### Backend (Python FastAPI)
```
neural_cli/
  main.py              # FastAPI app, WebSocket endpoint, REST API
  models.py            # Pydantic models (NeuralStatus, BrainRegion, etc.)
  file_watcher.py      # watchdog-based file monitoring
  test_analyzer.py     # pytest integration and test parsing
  metric_calculator.py # Illumination level calculations

neural_core.py         # Universal startup script (auto-installs deps)
```

### Communication Flow
1. Backend watches files via `watchdog`
2. File changes trigger test runs via `pytest`
3. Results update `NeuralStatus` model
4. WebSocket broadcasts to frontend (`ws://localhost:8000/ws`)
5. Frontend updates 3D brain illumination via `useBrainState`

---

## Tech Stack

**Frontend:** React 19, Three.js/R3F, Tailwind CSS (cyberpunk palette), Lucide Icons, Vitest
**Backend:** Python 3.8+, FastAPI, uvicorn, watchdog, pytest
**Build:** Vite, TypeScript

---

## Critical Rules

### Standards Globaux (Référence)

Les règles ci-dessous sont conformes aux standards globaux définis dans `~/.claude/standards/`.

### TypeScript — Règle ABSOLUE

> **Référence** : `~/.claude/standards/tsconfig.strict.json`

**STRICTEMENT INTERDIT** :
- ❌ Cast `as` (e.g., `value as SomeType`)
- ❌ `any` explicite ou implicite
- ❌ Non-null assertion `!`

**OBLIGATOIRE** :
- ✅ Zod avec `safeParse()` pour validation runtime
- ✅ Type guards pour narrowing
- ✅ Génériques pour flexibilité typée

```typescript
// ❌ INTERDIT
const data = response as NeuralStatus;

// ✅ OBLIGATOIRE
import { z } from "zod";
const NeuralStatusSchema = z.object({...});
const result = NeuralStatusSchema.safeParse(response);
if (!result.success) throw new ValidationError(result.error);
const data = result.data; // Type inféré correctement
```

### State Management Protocol
1. Before any code change: assess regression risk
2. If risk detected: start with `ALERT: POTENTIAL REGRESSION DETECTED`
3. After fixes: confirm with `Neural pathways restored. System optimal.`

### Test-Driven Illumination
- No test = No light in the neural visualization
- Every new module MUST have associated unit tests
- Test coverage directly correlates to brain illumination intensity

### Performance 3D (via `@ingenieur-graphique-3d`)

Pour toute question de performance de rendu :
- **Target** : 60 FPS constant
- **Techniques** : LOD, Instanced Rendering, Shader optimization
- **Profiling** : Chrome DevTools Performance tab, Three.js stats

---

## Key Files

- `neural_status.json` — Real-time status file (generated by backend, read by frontend)
- `neural_config.json` — Project configuration (the "soul")
- `tailwind.config.js` — Cyberpunk color palette definitions
- `vite.config.ts` — Three.js chunking optimization

---

## Ports

- **5173** — Vite dev server (frontend)
- **8000** — FastAPI (backend + WebSocket)

---

## Délégation aux Agents

| Tâche | Agent à invoquer |
|-------|------------------|
| Rendu 3D, shaders, performance GPU | `@ingenieur-graphique-3d` |
| Frontend React, hooks, state | `@developpeur-fullstack` |
| Backend FastAPI, WebSocket | `@developpeur-fullstack` |
| Tests Vitest/pytest, coverage | `@ingenieur-qa-automation` |
| Architecture système | `@architecte-principal` |
| CI/CD, Docker | `@ingenieur-devops` |
