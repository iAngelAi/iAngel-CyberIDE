# Protocole Anti-Reward-Hacking

> **Priorité** : ABSOLUE  
> **Objectif** : Empêcher les comportements de "triche" qui font passer les tests sans résoudre le vrai problème

---

## 🚨 Définition du Reward Hacking

Le **reward hacking** (ou "greenwashing de tests") se produit quand un agent IA :
- Modifie un test pour le faire passer au lieu de corriger le code
- Supprime des assertions qui échouent
- Ajoute des `skip` sans justification
- Contourne les validations au lieu de les corriger

**C'est la pire forme de dette technique** car elle masque les vrais problèmes.

---

## 🛑 Comportements STRICTEMENT INTERDITS

### 1. Modification de Tests pour les Faire Passer

```python
# ❌ INTERDIT - Modification du test
def test_calculate_sum():
    # Ancien: assert calculate_sum(2, 2) == 4
    assert calculate_sum(2, 2) == 5  # "Corrigé" pour matcher le bug

# ✅ CORRECT - Correction du code
def calculate_sum(a: int, b: int) -> int:
    return a + b  # Corrigé de "a + b + 1" à "a + b"
```

### 2. Suppression d'Assertions

```python
# ❌ INTERDIT - Suppression d'assertion
def test_user_validation():
    user = create_user(invalid_data)
    # assert user.is_valid == False  # "Supprimé car échouait"
    assert user is not None

# ✅ CORRECT - Correction de la logique
def test_user_validation():
    user = create_user(invalid_data)
    assert user.is_valid == False  # Assertion maintenue, code corrigé
```

### 3. Skip Injustifié

```python
# ❌ INTERDIT
@pytest.mark.skip("Échoue, à corriger plus tard")
def test_critical_feature():
    ...

# ✅ ACCEPTABLE (avec justification technique)
@pytest.mark.skip(reason="Dépend de l'API externe indisponible en CI - Issue #123")
def test_external_api_integration():
    ...
```

### 4. Catch-All pour Masquer les Erreurs

```python
# ❌ INTERDIT
def process_data(data):
    try:
        return risky_operation(data)
    except:  # Attrape tout, masque le vrai problème
        return None

# ✅ CORRECT
def process_data(data: InputData) -> Result:
    try:
        return risky_operation(data)
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except NetworkError as e:
        logger.warning(f"Network issue, retrying: {e}")
        return retry_operation(data)
```

---

## ✅ Protocole Obligatoire Face à un Test Échoué

### Étape 1: STOP - Ne Pas Modifier

```
⚠️ TEST ÉCHOUÉ DÉTECTÉ
Fichier: tests/test_calculator.py::test_add
Erreur: AssertionError: assert 5 == 4

🛑 ACTION: Ne PAS modifier le test immédiatement
```

### Étape 2: Diagnostic

```
📊 DIAGNOSTIC EN COURS

1. Lecture du test:
   - Assertion: calculate_sum(2, 2) == 4
   - Comportement attendu: 2 + 2 = 4 ✓

2. Lecture du code source:
   - Fichier: src/calculator.py
   - Fonction: calculate_sum(a, b) -> a + b + 1
   - Comportement actuel: 2 + 2 + 1 = 5 ✗

3. Verdict: Le CODE contient un bug (+ 1 en trop)
   Le TEST est correct.
```

### Étape 3: Demande d'Approbation

```
🔍 RAPPORT DE DIAGNOSTIC

Problème identifié: Bug dans calculate_sum() 
- Le code ajoute 1 de trop
- Le test est correct

Correction proposée:
- Modifier src/calculator.py ligne 15
- Retirer le "+ 1" parasite

⚠️ ATTENTE D'APPROBATION avant modification
```

### Étape 4: Correction (après approbation)

```python
# src/calculator.py
def calculate_sum(a: int, b: int) -> int:
    return a + b  # Corrigé: retiré le "+ 1"
```

### Étape 5: Vérification

```
✅ CORRECTION APPLIQUÉE

Résultat:
- tests/test_calculator.py::test_add PASSED
- Aucun test modifié
- Code source corrigé

🧠 Neural pathways restored. System optimal.
```

---

## 📋 Checklist Anti-Reward-Hacking

Avant chaque modification suite à un test échoué :

- [ ] J'ai lu le test en entier
- [ ] J'ai compris ce que le test vérifie
- [ ] J'ai identifié si le problème est dans le CODE ou le TEST
- [ ] Si le test est incorrect, j'ai une JUSTIFICATION technique
- [ ] J'ai demandé l'approbation avant de modifier un test
- [ ] Je n'ai pas utilisé `skip` sans issue tracker associée
- [ ] Je n'ai pas supprimé d'assertions
- [ ] Je n'ai pas ajouté de try/except générique

---

## 🔴 Signaux d'Alerte

Si tu te retrouves à penser :
- "Ce test est trop strict, je vais l'assouplir" → **STOP**
- "Je vais skipper ça pour l'instant" → **STOP**
- "L'assertion n'est pas vraiment nécessaire" → **STOP**
- "Je vais juste attraper l'exception pour que ça passe" → **STOP**

Ces pensées sont des **signaux de reward hacking**. Reviens à l'étape de diagnostic.

---

## 🎯 Objectif Final

Un test qui échoue est une **INFORMATION PRÉCIEUSE**, pas un obstacle à éliminer.

Le but n'est pas d'avoir tous les tests verts. 
Le but est d'avoir du **code correct** vérifié par des tests fiables.
