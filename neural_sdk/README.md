# Neural SDK

Le **Neural SDK** est la couche de connectivité qui transforme votre code Python statique en un organisme vivant et observable.

## Installation

```bash
pip install -e ./neural_sdk
```

## Utilisation

### Décorateur (Recommandé)

Utilisez `@neural_synapse` pour connecter vos fonctions importantes au cortex visuel.

```python
from neural_sdk import neural_synapse

@neural_synapse(region="backend", layer="auth")
def authenticate_user(username, password):
    # Quand cette fonction s'exécute, le neurone correspondant s'illumine.
    # En cas d'erreur, il pulse en rouge.
    pass
```

### Context Manager

Pour des blocs de code spécifiques :

```python
from neural_sdk import NeuralContext

def process_data():
    # ... code non tracé ...
    
    with NeuralContext("data_pipeline", "processing"):
        # Ce bloc sera visualisé comme une impulsion neuronale
        heavy_computation()
```

## Architecture

Le SDK utilise des sockets UDP non-bloquants ("Fire and Forget") pour envoyer des télémétries au **Neural Core** local (port 8123). L'impact sur les performances de votre application est négligeable (< 0.1ms).
