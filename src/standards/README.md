# Standards TypeScript — Règles Fil

Ce dossier contient les standards de code TypeScript stricts pour le projet CyberIDE.

## Configuration TypeScript (`tsconfig.strict.json`)

### Options de compilation strictes

| Option | Valeur | Description |
|--------|--------|-------------|
| `strict` | `true` | Active toutes les vérifications strictes |
| `noImplicitAny` | `true` | Interdit les types `any` implicites |
| `strictNullChecks` | `true` | `null` et `undefined` doivent être gérés explicitement |
| `noUncheckedIndexedAccess` | `true` | Les accès par index peuvent être `undefined` |
| `exactOptionalPropertyTypes` | `true` | Distinction entre `undefined` et propriété absente |
| `noUnusedLocals` | `true` | Variables locales non utilisées = erreur |
| `noUnusedParameters` | `true` | Paramètres non utilisés = erreur |

### Cible de compilation
- **`target: ES2022`** — Fonctionnalités JavaScript modernes
- **`module: NodeNext`** — Résolution de modules ESM native

## Règles Fil — ABSOLUMENT INTERDITS

### ❌ Cast `as`
```typescript
// INTERDIT
const data = response as NeuralStatus;

// OBLIGATOIRE — Utiliser Zod
import { z } from "zod";
const NeuralStatusSchema = z.object({...});
const result = NeuralStatusSchema.safeParse(response);
if (!result.success) throw new ValidationError(result.error);
const data = result.data;
```

### ❌ Type `any`
```typescript
// INTERDIT
function process(data: any): any { ... }

// OBLIGATOIRE — Types explicites ou génériques
function process<T extends BaseData>(data: T): ProcessedData<T> { ... }
```

### ❌ Non-null assertion `!`
```typescript
// INTERDIT
const value = maybeNull!.property;

// OBLIGATOIRE — Vérification explicite
if (maybeNull === null) throw new Error("Value required");
const value = maybeNull.property;

// OU — Optional chaining avec fallback
const value = maybeNull?.property ?? defaultValue;
```

## Utilisation

### Étendre cette configuration

Dans votre `tsconfig.json` :

```json
{
  "extends": "./src/standards/tsconfig.strict.json",
  "compilerOptions": {
    // Options spécifiques au projet
  }
}
```

### Vérifier le code

```bash
# Vérification TypeScript
npx tsc --noEmit

# Avec ESLint
npm run lint
```

## Philosophie Fil

> **"Le système de types est votre première ligne de défense."**

Ces règles strictes garantissent :

1. **🛡️ Sécurité de type** — Aucune faille dans le système de types
2. **🔍 Null-safety** — `null` et `undefined` toujours gérés
3. **📝 Documentation vivante** — Les types documentent le code
4. **🐛 Moins de bugs** — Erreurs détectées à la compilation

## Validation Runtime avec Zod

Les types TypeScript ne protègent qu'à la compilation. Pour les données externes (API, WebSocket, fichiers), utilisez **Zod** :

```typescript
import { z } from "zod";

// Schéma de validation
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(["admin", "user", "guest"]),
});

// Type inféré automatiquement
type User = z.infer<typeof UserSchema>;

// Validation sécurisée
function processUser(input: unknown): User {
  const result = UserSchema.safeParse(input);
  if (!result.success) {
    throw new ValidationError(result.error.flatten());
  }
  return result.data; // Type User garanti
}
```

## Intégration avec le projet CyberIDE

Ces standards s'intègrent avec :
- **`src/schemas/`** — Schémas Zod pour validation WebSocket
- **`src/types/`** — Types TypeScript du projet
- **`vitest`** — Tests unitaires avec types stricts
