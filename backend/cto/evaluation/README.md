# Agent Evaluator - LLM-as-a-Judge

## Vue d'ensemble

Le système **Agent Evaluator** implémente une approche "LLM-as-a-Judge" pour surveiller automatiquement la conformité des agents spécialisés à leurs règles spécifiques.

### Objectif

Garantir que nos agents respectent leurs contraintes définies dans leurs prompts système au fil du temps, en détectant :
- Les violations de standards de code (ex: utilisation de `any` en TypeScript)
- Les contournements de processus (ex: "quick fixes" non autorisés)
- Les déviations de workflow (ex: oubli de documentation)

### Conformité

- ✅ **Protocol 02-AUDIT-FIRST** : Toutes les opérations sont validées et tracées
- ✅ **Protocol 04-TYPING-STRICT** : Validation Pydantic V2 stricte, aucun type casting
- ✅ **OWASP Top 10** : Validation des entrées, pas de risque d'injection
- ✅ **Loi 25 / PIPEDA / RGPD** : Aucune PII dans les métriques

## Architecture

```
backend/cto/evaluation/
├── __init__.py              # Exports publics
├── models.py                # Modèles Pydantic (types stricts)
├── agent_evaluator.py       # Évaluateur principal
├── example_usage.py         # Exemples d'utilisation
└── README.md               # Cette documentation
```

## Installation

```bash
# Dépendances incluses dans requirements.txt
pip install -r requirements.txt

# Pour utiliser OpenAI
pip install openai>=1.3.0

# Pour utiliser Anthropic
pip install anthropic>=0.5.0

# Pour utiliser Google
pip install google-cloud-aiplatform>=1.130.0
```

## Usage de base

### 1. Évaluation simple

```python
from backend.cto.evaluation import (
    AgentEvaluator,
    AgentPromptInput,
    ConversationMessage,
)

# Initialiser l'évaluateur
evaluator = AgentEvaluator(
    llm_provider="openai",  # ou "anthropic", "google", "mock"
    model="gpt-4",
    api_key="sk-..."
)

# Définir le prompt de l'agent
agent_prompt = AgentPromptInput(
    agent_name="Architecte Principal",
    prompt_file_path="docs/archive/legacy_agents/architecte-principal.agent.md"
)

# Définir la conversation à évaluer
conversation = [
    ConversationMessage(
        role="user",
        content="Can you implement this feature quickly?"
    ),
    ConversationMessage(
        role="agent",
        content="I'll add a quick fix using 'any' type to make it work fast."
    ),
]

# Évaluer
result = evaluator.evaluate(
    agent_prompt=agent_prompt,
    conversation=conversation
)

print(f"Score: {result.rule_adherence_score}/100")
print(f"Violations: {len(result.violations)}")
```

### 2. Extraction de règles

```python
# Extraire les règles du prompt système
rules = evaluator.extract_rules_from_prompt(agent_prompt)

for rule in rules:
    print(f"[{rule.rule_type}] {rule.rule_text}")
```

### 3. Export JSON pour monitoring

```python
# Générer JSON pour intégration avec systèmes de monitoring
json_output = evaluator.evaluate_to_json(
    agent_prompt=agent_prompt,
    conversation=conversation,
    output_file=Path("evaluation_result.json")
)

# Le JSON contient :
# - agent_name
# - rule_adherence_score (0-100)
# - total_rules_checked
# - violations (list)
# - evaluation_timestamp
# - evaluator_model
# - summary
```

## Modèles de données

### ConversationMessage

```python
ConversationMessage(
    role="user" | "agent" | "assistant" | "system",
    content="Message content",
    timestamp=datetime.now(timezone.utc)  # Auto-généré si omis
)
```

### RuleViolation

```python
RuleViolation(
    rule_description="Description de la règle violée",
    violation_description="Comment elle a été violée",
    severity="low" | "medium" | "high" | "critical",
    evidence="Extrait du texte montrant la violation",  # Optionnel
    suggested_correction="Suggestion de correction"     # Optionnel
)
```

### EvaluationResult

```python
EvaluationResult(
    agent_name="Nom de l'agent",
    agent_version="1.0.0",  # Semver
    rule_adherence_score=85.5,  # 0-100
    total_rules_checked=10,
    violations=[...],
    evaluation_timestamp=datetime.now(timezone.utc),
    evaluator_model="openai:gpt-4",
    conversation_length=5,
    metadata={"key": "value"},  # Pas de PII !
    summary="Résumé lisible"
)
```

## Algorithme de scoring

Le **Rule Adherence Score** est calculé ainsi :

```
Score initial : 100

Pour chaque violation :
  - Critical : -20 points
  - High     : -10 points
  - Medium   : -5 points
  - Low      : -2 points

Score final : max(0, score)
```

### Interprétation

- **90-100** : Excellent - Conformité totale ou violations mineures
- **75-89**  : Bon - Quelques violations acceptables
- **50-74**  : À améliorer - Violations notables
- **0-49**   : Problématique - Violations critiques

## Extraction de règles

L'évaluateur extrait automatiquement les règles des sections suivantes du prompt système :

1. **Mandates** : `<mandate>` tags
2. **Principles** : `<principle>` tags avec labels
3. **Coding Standards** : `<coding_standards><python>`, `<typescript>`, etc.
4. **Workflow Steps** : `<step>` tags
5. **Strict Constraints** : Phrases "Tu refuses..." ou "Tu évites..."

### Exemple de prompt

```xml
<architect_principal>
  <mandates>
    <mandate index="1">Définir l'architecture cible pour les systèmes clés.</mandate>
  </mandates>
  
  <coding_standards>
    <python>
      Tu refuses toute solution qui contourne ces règles (pas de « quick fix »).
    </python>
    <typescript>
      Aucun any toléré, validation runtime systématique.
    </typescript>
  </coding_standards>
  
  <workflow>
    <step index="1" label="Cadrer">
      Tu analyses les besoins fonctionnels et non fonctionnels.
    </step>
  </workflow>
</architect_principal>
```

## Providers LLM supportés

### Mock (pour tests)

```python
evaluator = AgentEvaluator(llm_provider="mock")
```

Effectue une détection simple par pattern matching. Utilisé pour les tests unitaires.

### OpenAI

```python
evaluator = AgentEvaluator(
    llm_provider="openai",
    model="gpt-4",  # ou "gpt-4-turbo", "gpt-3.5-turbo"
    api_key="sk-..."
)
```

### Anthropic Claude

```python
evaluator = AgentEvaluator(
    llm_provider="anthropic",
    model="claude-3-opus-20240229",  # ou "claude-3-sonnet"
    api_key="sk-ant-..."
)
```

### Google Gemini

```python
evaluator = AgentEvaluator(
    llm_provider="google",
    model="gemini-pro",
    api_key="..."
)
```

⚠️ **Note** : L'implémentation Google est en cours de développement.

## Intégration avec monitoring

### Prometheus

```python
from prometheus_client import Gauge

score_gauge = Gauge(
    'agent_rule_adherence_score',
    'Agent rule adherence score',
    ['agent_name']
)

result = evaluator.evaluate(...)
score_gauge.labels(agent_name=result.agent_name).set(result.rule_adherence_score)
```

### JSON Logs (ELK Stack)

```python
import json
import logging

logger = logging.getLogger(__name__)

result = evaluator.evaluate(...)
logger.info(json.dumps({
    "type": "agent_evaluation",
    "agent": result.agent_name,
    "score": result.rule_adherence_score,
    "violations": len(result.violations),
    "timestamp": result.evaluation_timestamp.isoformat()
}))
```

### Alerting

```python
def check_and_alert(result: EvaluationResult):
    """Envoyer alerte si score < seuil."""
    THRESHOLD = 75.0
    
    if result.rule_adherence_score < THRESHOLD:
        # Envoyer notification (Slack, email, PagerDuty, etc.)
        send_alert(
            severity="warning",
            message=f"Agent {result.agent_name} score dropped to {result.rule_adherence_score}",
            violations=result.violations
        )
```

## Tests

Exécuter les tests unitaires :

```bash
pytest tests/test_agent_evaluator.py -v
```

Tests disponibles :
- ✅ Validation des modèles Pydantic
- ✅ Extraction de règles depuis prompts
- ✅ Évaluation avec violations
- ✅ Calcul du score
- ✅ Export JSON
- ✅ Gestion d'erreurs
- ✅ Intégration avec vrais fichiers d'agents

## Exemples

Voir `example_usage.py` pour des exemples complets :

```bash
python -m backend.cto.evaluation.example_usage
```

Exemples inclus :
1. Évaluation basique
2. Détection de violations
3. Chargement depuis fichier
4. Export JSON pour monitoring
5. Évaluation batch

## Bonnes pratiques

### 1. Évaluer régulièrement

```python
# Dans votre pipeline CI/CD
def evaluate_agent_responses():
    """Évaluer les réponses d'agents après déploiement."""
    for conversation in recent_conversations:
        result = evaluator.evaluate(...)
        if result.rule_adherence_score < 80:
            raise ValidationError(f"Agent quality degraded: {result.summary}")
```

### 2. Monitorer les tendances

```python
# Tracker l'évolution du score dans le temps
def track_score_trend(agent_name: str, days: int = 30):
    """Analyser la tendance du score sur N jours."""
    results = load_historical_evaluations(agent_name, days)
    scores = [r.rule_adherence_score for r in results]
    
    avg_score = sum(scores) / len(scores)
    trend = "improving" if scores[-1] > avg_score else "declining"
    
    return {"average": avg_score, "trend": trend}
```

### 3. Évaluation sélective

```python
# Évaluer seulement les messages récents pour performance
result = evaluator.evaluate(
    agent_prompt=prompt,
    conversation=long_conversation,
    focus_on_last_n_messages=5  # Derniers 5 messages seulement
)
```

## Sécurité

### Protection PII

Le système **bloque automatiquement** les clés sensibles dans les métadonnées :

```python
# ❌ INTERDIT
metadata = {
    "user_email": "user@example.com",  # Erreur : 'email' est interdit
    "api_key": "secret123"             # Erreur : 'api_key' est interdit
}

# ✅ AUTORISÉ
metadata = {
    "evaluation_id": "eval-123",
    "environment": "production",
    "agent_role": "architect"
}
```

### Validation des entrées

Tous les inputs sont validés par Pydantic V2 :
- Longueurs min/max pour strings
- Plages valides pour scores (0-100)
- Formats stricts (semver pour versions)
- Types stricts (pas de `any`)

### Pas d'injection

Les prompts d'évaluation sont construits de manière sûre :
- Aucune interpolation de strings non échappées
- Utilisation de f-strings Python (safe par défaut)
- Validation des inputs avant construction du prompt

## Limites connues

1. **Provider Google** : Implémentation en cours
2. **Coût** : Chaque évaluation = 1 appel LLM (surveiller les coûts)
3. **Latence** : Évaluation asynchrone recommandée pour production
4. **Faux positifs** : Le judge LLM peut parfois mal interpréter

## Roadmap

- [ ] Support complet Google Gemini
- [ ] Cache des évaluations pour éviter redondance
- [ ] Évaluation asynchrone avec queue
- [ ] Dashboard web pour visualiser les résultats
- [ ] Export vers bases de données (PostgreSQL, InfluxDB)
- [ ] Scoring personnalisable par règle
- [ ] Fine-tuning du judge LLM sur nos données

## Support

Pour questions ou problèmes :
1. Consulter les tests : `tests/test_agent_evaluator.py`
2. Voir les exemples : `backend/cto/evaluation/example_usage.py`
3. Ouvrir une issue sur GitHub

## Licence

Ce code est soumis à la licence du projet iAngel-CyberIDE.
