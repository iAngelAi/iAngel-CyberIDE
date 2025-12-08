# 🤖 Guide de Sécurité des Systèmes IA — CyberIDE

<div align="center">

**Version 1.0.0** | Décembre 2024

*"Secure AI: From Training to Inference"*

</div>

---

## 📋 Vue d'Ensemble

Ce guide couvre les aspects de sécurité spécifiques aux systèmes d'intelligence artificielle et d'apprentissage automatique utilisés dans le CyberIDE.

**Périmètre:**
- Modèles d'IA utilisés pour l'analyse de code
- Agents IA de l'architecture multi-agents
- Intégrations avec LLMs externes (Claude, GPT-4, etc.)
- Données d'entraînement et pipelines ML

---

## 🎯 Risques Spécifiques à l'IA

### 1. Risques de Sécurité Traditionnels

| Risque | Description | Mitigation |
|--------|-------------|------------|
| **Empoisonnement de données** | Injection de données malveillantes dans training set | Validation stricte, provenance tracking |
| **Attaques adversariales** | Inputs craftés pour tromper le modèle | Détection d'anomalies, input validation |
| **Extraction de modèle** | Vol de la propriété intellectuelle du modèle | Rate limiting, watermarking |
| **Inversion de modèle** | Reconstruction des données d'entraînement | Differential privacy, minimisation |
| **Déni de service** | Surcharge du modèle avec requêtes coûteuses | Rate limiting, resource caps |

### 2. Risques de Confidentialité

| Risque | Description | Mitigation |
|--------|-------------|------------|
| **Mémorisation de PII** | Modèle mémorise des données personnelles | Anonymisation, filtrage pré-traitement |
| **Fuite de données** | Extraction d'infos sensibles via prompts | Output filtering, content moderation |
| **Inférence d'appartenance** | Déterminer si une donnée était dans training set | Differential privacy, agrégation |

### 3. Risques Éthiques et de Biais

| Risque | Description | Mitigation |
|--------|-------------|------------|
| **Biais algorithmiques** | Discrimination basée sur des attributs protégés | Fairness testing, débiasing |
| **Amplification de stéréotypes** | Renforcement de préjugés sociétaux | Diverse training data, monitoring |
| **Décisions opaques** | Manque de transparence/explicabilité | Explainable AI (XAI), audits |

---

## 🛡️ Sécurité du Cycle de Vie ML

### Phase 1: Collecte et Préparation des Données

#### Validation des Données d'Entraînement

```python
from typing import List, Dict
from pydantic import BaseModel, Field, validator
import hashlib

class TrainingDataset(BaseModel):
    """Validated training dataset metadata."""
    
    name: str = Field(..., min_length=1)
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')
    source: str = Field(..., description="Provenance of data")
    size_records: int = Field(..., gt=0)
    checksum: str = Field(..., regex=r'^[a-f0-9]{64}$')
    contains_pii: bool = False
    anonymization_applied: bool = False
    
    @validator('checksum')
    def validate_integrity(cls, v, values):
        """Verify data hasn't been tampered with."""
        # In real implementation, verify against actual data
        return v
    
    def verify_integrity(self, data_path: str) -> bool:
        """Verify dataset hasn't been modified."""
        with open(data_path, 'rb') as f:
            calculated_checksum = hashlib.sha256(f.read()).hexdigest()
        return calculated_checksum == self.checksum

# Usage
dataset = TrainingDataset(
    name="code-analysis-dataset",
    version="1.2.0",
    source="github-public-repos",
    size_records=100000,
    checksum="abc123...",
    contains_pii=False,
    anonymization_applied=True
)
```

#### Anonymisation des Données

```python
import re
from typing import str

class PIIAnonymizer:
    """Anonymize PII in training data."""
    
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'api_key': r'(sk|pk|token)-[a-zA-Z0-9]{20,}',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    }
    
    def anonymize(self, text: str) -> str:
        """Remove PII from text."""
        anonymized = text
        
        for pii_type, pattern in self.PATTERNS.items():
            anonymized = re.sub(pattern, f'<{pii_type.upper()}_REDACTED>', anonymized)
        
        return anonymized
    
    def validate_no_pii(self, text: str) -> bool:
        """Check if text contains PII."""
        for pattern in self.PATTERNS.values():
            if re.search(pattern, text):
                return False
        return True

# Usage
anonymizer = PIIAnonymizer()

code_sample = """
user_email = "john.doe@example.com"
api_key = "sk-1234567890abcdefghijklmnop"
"""

anonymized_code = anonymizer.anonymize(code_sample)
# Output:
# user_email = "<EMAIL_REDACTED>"
# api_key = "<API_KEY_REDACTED>"
```

### Phase 2: Entraînement du Modèle

#### Differential Privacy

```python
import numpy as np
from typing import List

class DifferentialPrivacy:
    """Implement differential privacy for model training."""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Args:
            epsilon: Privacy budget (smaller = more private)
            delta: Failure probability
        """
        self.epsilon = epsilon
        self.delta = delta
    
    def add_noise(self, true_value: float, sensitivity: float) -> float:
        """Add Laplacian noise for differential privacy."""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return true_value + noise
    
    def clip_gradients(self, gradients: np.ndarray, clip_norm: float = 1.0) -> np.ndarray:
        """Clip gradients to limit sensitivity."""
        grad_norm = np.linalg.norm(gradients)
        if grad_norm > clip_norm:
            gradients = gradients * (clip_norm / grad_norm)
        return gradients

# Usage in training loop
dp = DifferentialPrivacy(epsilon=1.0)

def train_with_dp(model, data, labels):
    for epoch in range(num_epochs):
        for batch_x, batch_y in zip(data, labels):
            # Forward pass
            predictions = model(batch_x)
            loss = compute_loss(predictions, batch_y)
            
            # Backward pass with DP
            gradients = compute_gradients(loss)
            gradients = dp.clip_gradients(gradients)
            gradients = dp.add_noise(gradients, sensitivity=0.1)
            
            # Update model
            model.apply_gradients(gradients)
```

#### Monitoring de l'Entraînement

```python
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TrainingMetrics:
    """Metrics tracked during training."""
    epoch: int
    train_loss: float
    val_loss: float
    train_accuracy: float
    val_accuracy: float
    fairness_metric: float
    timestamp: datetime

class SecureTrainingMonitor:
    """Monitor training for security issues."""
    
    def __init__(self, alert_threshold: float = 0.1):
        self.metrics_history = []
        self.alert_threshold = alert_threshold
        self.logger = logging.getLogger(__name__)
    
    def log_metrics(self, metrics: TrainingMetrics):
        """Log metrics and check for anomalies."""
        self.metrics_history.append(metrics)
        
        # Check for sudden performance drop (possible poisoning)
        if len(self.metrics_history) > 1:
            prev = self.metrics_history[-2]
            accuracy_drop = prev.val_accuracy - metrics.val_accuracy
            
            if accuracy_drop > self.alert_threshold:
                self.logger.warning(
                    f"🚨 Possible data poisoning detected! "
                    f"Accuracy dropped by {accuracy_drop:.2%} at epoch {metrics.epoch}"
                )
        
        # Check fairness
        if metrics.fairness_metric < 0.8:
            self.logger.warning(
                f"⚠️ Fairness metric below threshold: {metrics.fairness_metric:.2f}"
            )

monitor = SecureTrainingMonitor()
```

### Phase 3: Validation et Tests

#### Tests de Robustesse (Adversarial)

```python
import numpy as np

class AdversarialTester:
    """Test model robustness against adversarial attacks."""
    
    def fgsm_attack(self, model, input_data, true_label, epsilon=0.01):
        """
        Fast Gradient Sign Method attack.
        
        Args:
            epsilon: Perturbation magnitude
        """
        # Get gradient of loss w.r.t input
        with torch.enable_grad():
            input_data.requires_grad = True
            output = model(input_data)
            loss = criterion(output, true_label)
            loss.backward()
        
        # Create perturbation
        perturbation = epsilon * input_data.grad.sign()
        adversarial_input = input_data + perturbation
        
        return adversarial_input
    
    def test_robustness(self, model, test_data, test_labels):
        """Test model against adversarial examples."""
        original_accuracy = evaluate(model, test_data, test_labels)
        
        adversarial_data = []
        for data, label in zip(test_data, test_labels):
            adv = self.fgsm_attack(model, data, label)
            adversarial_data.append(adv)
        
        adversarial_accuracy = evaluate(model, adversarial_data, test_labels)
        
        robustness_score = adversarial_accuracy / original_accuracy
        
        return {
            'original_accuracy': original_accuracy,
            'adversarial_accuracy': adversarial_accuracy,
            'robustness_score': robustness_score
        }

tester = AdversarialTester()
results = tester.test_robustness(model, test_data, test_labels)

if results['robustness_score'] < 0.8:
    print("⚠️ Model is vulnerable to adversarial attacks!")
```

#### Tests de Biais

```python
from sklearn.metrics import confusion_matrix
import pandas as pd

class FairnessAuditor:
    """Audit model for bias across protected attributes."""
    
    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes
    
    def demographic_parity(self, predictions, protected_attr):
        """
        Check if positive prediction rate is similar across groups.
        
        Metric: P(Y=1 | A=a) should be similar for all values of A
        """
        groups = {}
        for attr_value in set(protected_attr):
            mask = protected_attr == attr_value
            positive_rate = predictions[mask].mean()
            groups[attr_value] = positive_rate
        
        # Calculate disparity
        rates = list(groups.values())
        disparity = max(rates) - min(rates)
        
        return {
            'groups': groups,
            'disparity': disparity,
            'passed': disparity < 0.1  # 10% threshold
        }
    
    def equalized_odds(self, predictions, true_labels, protected_attr):
        """
        Check if TPR and FPR are similar across groups.
        """
        results = {}
        
        for attr_value in set(protected_attr):
            mask = protected_attr == attr_value
            cm = confusion_matrix(
                true_labels[mask],
                predictions[mask]
            )
            
            tpr = cm[1,1] / (cm[1,1] + cm[1,0])  # True Positive Rate
            fpr = cm[0,1] / (cm[0,1] + cm[0,0])  # False Positive Rate
            
            results[attr_value] = {'tpr': tpr, 'fpr': fpr}
        
        return results

# Usage
auditor = FairnessAuditor(protected_attributes=['gender', 'age_group'])

# Test demographic parity
dp_results = auditor.demographic_parity(predictions, gender_data)
if not dp_results['passed']:
    print(f"⚠️ Demographic parity violated! Disparity: {dp_results['disparity']:.2%}")
```

### Phase 4: Déploiement et Inférence

#### Input Validation

```python
from pydantic import BaseModel, Field, validator
import re

class CodeAnalysisRequest(BaseModel):
    """Validated request for AI code analysis."""
    
    code: str = Field(..., min_length=1, max_length=10000)
    language: str = Field(..., regex=r'^(python|typescript|javascript)$')
    analysis_type: str = Field(..., regex=r'^(security|quality|performance)$')
    
    @validator('code')
    def validate_no_malicious_patterns(cls, v):
        """Check for potentially malicious code patterns."""
        malicious_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'subprocess\.call',
            r'os\.system',
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Potentially malicious code pattern detected: {pattern}")
        
        return v
    
    @validator('code')
    def validate_no_secrets(cls, v):
        """Ensure no secrets in submitted code."""
        secret_patterns = {
            'api_key': r'(sk|pk|token)-[a-zA-Z0-9]{20,}',
            'password': r'password\s*=\s*["\'][^"\']+["\']',
        }
        
        for name, pattern in secret_patterns.items():
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Secret detected in code: {name}")
        
        return v

# Usage
try:
    request = CodeAnalysisRequest(
        code="def hello(): return 'world'",
        language="python",
        analysis_type="security"
    )
except ValidationError as e:
    print("❌ Invalid request:", e)
```

#### Output Filtering

```python
class OutputFilter:
    """Filter AI model outputs for sensitive content."""
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'api_key': r'(sk|pk|token)-[a-zA-Z0-9]{20,}',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        }
    
    def filter(self, output: str) -> Dict[str, any]:
        """Filter output and flag issues."""
        filtered = output
        flagged_patterns = []
        
        for pattern_name, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, output)
            if matches:
                flagged_patterns.append(pattern_name)
                filtered = re.sub(pattern, f'<{pattern_name.upper()}_REDACTED>', filtered)
        
        return {
            'filtered_output': filtered,
            'contained_pii': len(flagged_patterns) > 0,
            'flagged_patterns': flagged_patterns,
            'safe_to_display': len(flagged_patterns) == 0
        }

filter = OutputFilter()
result = filter.filter(model_output)

if not result['safe_to_display']:
    logging.warning(f"🚨 Model output contained PII: {result['flagged_patterns']}")
```

#### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/ai/analyze")
@limiter.limit("10/minute")  # Prevent model extraction attacks
async def analyze_code(request: CodeAnalysisRequest):
    """AI-powered code analysis endpoint."""
    
    # Validate input
    validated = CodeAnalysisRequest(**request.dict())
    
    # Run analysis (with timeout to prevent DoS)
    try:
        result = await asyncio.wait_for(
            run_ai_analysis(validated.code),
            timeout=30.0  # 30 second max
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Analysis timeout")
    
    # Filter output
    filtered = output_filter.filter(result)
    
    if not filtered['safe_to_display']:
        logging.warning("Model output contained PII, filtered")
    
    return {"analysis": filtered['filtered_output']}
```

---

## 🔒 Sécurité des Intégrations LLM

### OpenAI / Claude API

```python
from openai import OpenAI
from anthropic import Anthropic

class SecureLLMClient:
    """Secure wrapper for LLM API clients."""
    
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.pii_anonymizer = PIIAnonymizer()
    
    def sanitize_prompt(self, prompt: str) -> str:
        """Remove PII from prompts before sending to LLM."""
        return self.pii_anonymizer.anonymize(prompt)
    
    async def query_openai(self, prompt: str, system_prompt: str = None):
        """Query OpenAI with security measures."""
        
        # Sanitize input
        clean_prompt = self.sanitize_prompt(prompt)
        
        # Add security instructions to system prompt
        secure_system_prompt = (
            "You are a helpful assistant. "
            "NEVER generate, discuss, or output: "
            "API keys, passwords, personal information, harmful content. "
            + (system_prompt or "")
        )
        
        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": secure_system_prompt},
                    {"role": "user", "content": clean_prompt}
                ],
                max_tokens=1000,  # Limit output to control costs
                temperature=0.7,
            )
            
            # Filter output
            output = response.choices[0].message.content
            filtered = self.pii_anonymizer.anonymize(output)
            
            return filtered
            
        except Exception as e:
            logging.error(f"LLM API error: {e}")
            raise

client = SecureLLMClient()
```

### Prompt Injection Prevention

```python
class PromptInjectionDetector:
    """Detect and prevent prompt injection attacks."""
    
    INJECTION_PATTERNS = [
        r'ignore\s+(all\s+)?previous\s+instructions',
        r'disregard\s+.+\s+above',
        r'you\s+are\s+now\s+a\s+different',
        r'system\s*:\s*',
        r'<\|im_start\|>',  # Model-specific tokens
        r'###\s*Instruction',
    ]
    
    def is_injection_attempt(self, prompt: str) -> bool:
        """Check if prompt contains injection patterns."""
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False
    
    def sanitize_prompt(self, prompt: str) -> str:
        """Remove injection attempts from prompt."""
        # Remove markdown code blocks that might contain instructions
        prompt = re.sub(r'```.*?```', '', prompt, flags=re.DOTALL)
        
        # Remove XML-like tags
        prompt = re.sub(r'<[^>]+>', '', prompt)
        
        # Escape special characters
        prompt = prompt.replace('|', '\\|')
        
        return prompt

detector = PromptInjectionDetector()

user_prompt = input("Enter your prompt: ")

if detector.is_injection_attempt(user_prompt):
    print("🚨 Potential prompt injection detected! Request blocked.")
    logging.warning(f"Injection attempt: {user_prompt}")
else:
    sanitized = detector.sanitize_prompt(user_prompt)
    result = await llm_client.query(sanitized)
```

---

## 📊 Monitoring et Auditing

### Métriques de Sécurité IA

```python
from prometheus_client import Counter, Histogram, Gauge

# Métriques Prometheus
ml_requests_total = Counter(
    'ml_inference_requests_total',
    'Total ML inference requests',
    ['model', 'status']
)

ml_latency_seconds = Histogram(
    'ml_inference_latency_seconds',
    'ML inference latency',
    ['model']
)

ml_input_validation_failures = Counter(
    'ml_input_validation_failures_total',
    'Failed input validations',
    ['reason']
)

ml_output_pii_detections = Counter(
    'ml_output_pii_detections_total',
    'PII detected in model outputs',
    ['pii_type']
)

ml_adversarial_detections = Counter(
    'ml_adversarial_detections_total',
    'Potential adversarial inputs detected'
)

# Usage
@app.post("/api/ml/predict")
async def predict(request: PredictionRequest):
    start_time = time.time()
    
    try:
        # Validate input
        validated = PredictionRequest(**request.dict())
        
        # Run prediction
        result = model.predict(validated.data)
        
        # Filter output
        filtered = output_filter.filter(result)
        
        if filtered['contained_pii']:
            for pii_type in filtered['flagged_patterns']:
                ml_output_pii_detections.labels(pii_type=pii_type).inc()
        
        ml_requests_total.labels(model='code-analyzer', status='success').inc()
        
        return {"prediction": filtered['filtered_output']}
        
    except ValidationError as e:
        ml_input_validation_failures.labels(reason=str(e)).inc()
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        duration = time.time() - start_time
        ml_latency_seconds.labels(model='code-analyzer').observe(duration)
```

### Drift Detection

```python
import numpy as np
from scipy import stats

class DriftDetector:
    """Detect model drift over time."""
    
    def __init__(self, reference_distribution: np.ndarray):
        self.reference_distribution = reference_distribution
        self.reference_mean = np.mean(reference_distribution)
        self.reference_std = np.std(reference_distribution)
    
    def detect_drift(self, current_data: np.ndarray, threshold: float = 0.05) -> Dict:
        """
        Detect distribution drift using Kolmogorov-Smirnov test.
        
        Args:
            threshold: P-value threshold for drift detection
        """
        # KS test
        statistic, p_value = stats.ks_2samp(
            self.reference_distribution,
            current_data
        )
        
        drift_detected = p_value < threshold
        
        # Calculate magnitude of drift
        current_mean = np.mean(current_data)
        current_std = np.std(current_data)
        
        mean_shift = abs(current_mean - self.reference_mean) / self.reference_std
        
        return {
            'drift_detected': drift_detected,
            'p_value': p_value,
            'ks_statistic': statistic,
            'mean_shift': mean_shift,
            'recommendation': 'retrain_model' if drift_detected else 'continue_monitoring'
        }

# Usage - Monitor predictions over time
detector = DriftDetector(reference_predictions)

# Weekly check
current_predictions = get_recent_predictions(days=7)
drift_result = detector.detect_drift(current_predictions)

if drift_result['drift_detected']:
    logging.warning(
        f"🚨 Model drift detected! "
        f"P-value: {drift_result['p_value']:.4f}, "
        f"Mean shift: {drift_result['mean_shift']:.2f} std devs"
    )
    # Trigger retraining pipeline
```

---

## ✅ Checklist de Sécurité IA

### Données

- [ ] Données d'entraînement validées et checksumées
- [ ] PII anonymisées/pseudonymisées
- [ ] Provenance des données documentée
- [ ] Pas de données sensibles non autorisées
- [ ] Tests de qualité des données passés

### Modèle

- [ ] Tests de robustesse adversariale effectués
- [ ] Tests de biais et fairness effectués
- [ ] Differential privacy appliquée (si applicable)
- [ ] Versioning du modèle en place
- [ ] Model cards/documentation complètes

### Inférence

- [ ] Input validation stricte
- [ ] Output filtering activé
- [ ] Rate limiting configuré
- [ ] Timeout configuré
- [ ] Monitoring en place

### Intégrations

- [ ] APIs externes sécurisées (HTTPS, auth)
- [ ] Prompts sanitizés
- [ ] Protection contre injection
- [ ] Secrets gérés correctement
- [ ] Logs ne contiennent pas de PII

### Conformité

- [ ] AI Act requirements identifiés
- [ ] Documentation de transparence
- [ ] Audit trail complet
- [ ] Procédure de contestation en place
- [ ] Révision éthique effectuée

---

## 📚 Ressources

### Standards et Frameworks

- **NIST AI Risk Management Framework**: https://www.nist.gov/itl/ai-risk-management-framework
- **ISO/IEC 42001 AI Management System**: https://www.iso.org/standard/81230.html
- **EU AI Act**: https://artificialintelligenceact.eu/
- **OWASP Machine Learning Security Top 10**: https://owasp.org/www-project-machine-learning-security-top-10/

### Outils

- **Adversarial Robustness Toolbox (ART)**: https://github.com/Trusted-AI/adversarial-robustness-toolbox
- **Fairlearn**: https://fairlearn.org/
- **What-If Tool**: https://pair-code.github.io/what-if-tool/
- **TensorFlow Privacy**: https://github.com/tensorflow/privacy

### Formation

- **Stanford CS329S: Machine Learning Systems Design**: https://stanford-cs329s.github.io/
- **Google's Responsible AI Practices**: https://ai.google/responsibilities/responsible-ai-practices/
- **Microsoft's Responsible AI Resources**: https://www.microsoft.com/en-us/ai/responsible-ai

---

<div align="center">

**🤖 Secure AI = Trustworthy AI 🤖**

*"Intelligence without security is dangerous."*

</div>
