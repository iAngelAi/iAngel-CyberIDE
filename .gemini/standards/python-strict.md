# Python Standards — Pydantic V2 & Typage Strict

> **Priorité** : CRITIQUE
> **Applicable** : Tous fichiers `.py`

---

## Dependency Management (uv)

**CRITICAL**: `pip install` is FORBIDDEN. Use `uv` exclusively.

### Commands

```bash
# FORBIDDEN
pip install <package>
pip3 install <package>

# REQUIRED
uv add <package>           # Add dependency (updates uv.lock)
uv add --dev <package>     # Add dev dependency
uv sync                    # Install from lockfile
uv sync --frozen           # CI/CD (fails if lockfile outdated)
uv run python script.py    # Run with venv
uv run pytest              # Run tests
```

### Lockfile Authority

- `uv.lock` MUST be committed to git
- `uv.lock` guarantees reproducible builds
- CI/CD MUST use `uv sync --frozen`

---

## Configuration mypy

```ini
# pyproject.toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_explicit = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
```

---

## Patterns INTERDITS

### ❌ typing.Any
```python
# INTERDIT
from typing import Any

def process(data: Any) -> Any:
    return data

config: Any = load_config()
```

### ❌ Dict sans typage précis
```python
# INTERDIT
def get_user() -> dict:
    return {"name": "John", "age": 30}

def process(data: dict) -> dict:
    return data
```

### ❌ Type ignore sans justification
```python
# INTERDIT
result = some_function()  # type: ignore
```

---

## Patterns OBLIGATOIRES

### ✅ Pydantic V2 Models
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class User(BaseModel):
    model_config = ConfigDict(strict=True)
    
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### ✅ Validation avec model_validate
```python
from pydantic import ValidationError

def process_user(data: dict[str, object]) -> User:
    try:
        return User.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid user data: {e}")
```

### ✅ TypedDict pour dicts structurés
```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: str
    name: str
    email: str
    age: NotRequired[int]

def create_user_dict(name: str, email: str) -> UserDict:
    return {
        "id": generate_id(),
        "name": name,
        "email": email,
    }
```

### ✅ Génériques typés
```python
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None

# Usage
response: ApiResponse[User] = ApiResponse(success=True, data=user)
```

---

## FastAPI avec Typage Strict

### ✅ Endpoints typés
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest) -> UserResponse:
    user = await user_service.create(request)
    return UserResponse.model_validate(user)
```

### ✅ Dépendances typées
```python
from fastapi import Depends
from typing import Annotated

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/me")
async def get_me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
```

---

## Gestion d'Erreurs Typée

```python
from typing import Never

class AppError(Exception):
    def __init__(self, message: str, code: str) -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str) -> None:
        super().__init__(f"{resource} {id} not found", "NOT_FOUND")

def get_user_or_raise(user_id: str) -> User:
    user = db.get_user(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

---

## Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ANN",    # flake8-annotations
    "S",      # flake8-bandit (security)
    "BLE",    # flake8-blind-except
    "FBT",    # flake8-boolean-trap
    "A",      # flake8-builtins
    "COM",    # flake8-commas
    "C90",    # mccabe complexity
    "DJ",     # flake8-django
    "EM",     # flake8-errmsg
    "EXE",    # flake8-executable
    "ISC",    # flake8-implicit-str-concat
    "ICN",    # flake8-import-conventions
    "G",      # flake8-logging-format
    "INP",    # flake8-no-pep420
    "PIE",    # flake8-pie
    "T20",    # flake8-print
    "PYI",    # flake8-pyi
    "PT",     # flake8-pytest-style
    "Q",      # flake8-quotes
    "RSE",    # flake8-raise
    "RET",    # flake8-return
    "SLF",    # flake8-self
    "SIM",    # flake8-simplify
    "TID",    # flake8-tidy-imports
    "TCH",    # flake8-type-checking
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate
    "PL",     # Pylint
    "TRY",    # tryceratops
    "RUF",    # Ruff-specific rules
]
```
