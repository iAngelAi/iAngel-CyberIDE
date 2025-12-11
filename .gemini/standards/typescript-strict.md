# TypeScript Standards — Typage Strict

> **Priorité** : CRITIQUE  
> **Applicable** : Tous fichiers `.ts`, `.tsx`

---

## Configuration tsconfig.json

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true
  }
}
```

---

## Patterns INTERDITS

### ❌ Cast `as`
```typescript
// INTERDIT
const data = response as UserData;
const element = event.target as HTMLInputElement;
```

### ❌ Type `any`
```typescript
// INTERDIT
function process(data: any): any { ... }
let config: any = {};
```

### ❌ Non-null assertion `!`
```typescript
// INTERDIT
const element = document.getElementById('app')!;
const value = obj.prop!.nested!.value;
```

### ❌ Type assertions dans JSX
```typescript
// INTERDIT
<Component data={value as Props} />
```

---

## Patterns OBLIGATOIRES

### ✅ Validation Zod avec safeParse
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});

type User = z.infer<typeof UserSchema>;

function processUser(input: unknown): User {
  const result = UserSchema.safeParse(input);
  if (!result.success) {
    throw new ValidationError(result.error.format());
  }
  return result.data;
}
```

### ✅ Type Guards
```typescript
function isUser(value: unknown): value is User {
  return UserSchema.safeParse(value).success;
}

// Utilisation
if (isUser(data)) {
  console.log(data.name); // Type-safe
}
```

### ✅ Narrowing avec vérifications
```typescript
function getElement(id: string): HTMLElement {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Element ${id} not found`);
  }
  return element;
}
```

### ✅ Génériques typés
```typescript
async function fetchData<T extends z.ZodType>(
  url: string,
  schema: T
): Promise<z.infer<T>> {
  const response = await fetch(url);
  const json: unknown = await response.json();
  return schema.parse(json);
}
```

---

## Validation aux Frontières

### API Responses
```typescript
const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.unknown(),
  error: z.string().optional(),
});

async function apiCall(endpoint: string) {
  const response = await fetch(endpoint);
  const json: unknown = await response.json();
  const validated = ApiResponseSchema.parse(json);
  return validated;
}
```

### User Input
```typescript
const FormSchema = z.object({
  username: z.string().min(3).max(20),
  password: z.string().min(8),
});

function handleSubmit(formData: FormData) {
  const input = {
    username: formData.get('username'),
    password: formData.get('password'),
  };
  const result = FormSchema.safeParse(input);
  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }
  // Proceed with validated data
}
```

---

## ESLint Rules Recommandées

```json
{
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-non-null-assertion": "error",
    "@typescript-eslint/consistent-type-assertions": [
      "error",
      { "assertionStyle": "never" }
    ],
    "@typescript-eslint/strict-boolean-expressions": "error"
  }
}
```
