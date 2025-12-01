# Filtres Avancés des Pulses Git

## Cas d'Utilisation

### 1. Analyse de Projet Récent

```python
# Récupérer les 10 derniers commits du mois
recent_commits = pulse_engine._get_git_pulses(
    limit=10,
    since='1 month ago'
)
```

### 2. Suivi des Activités d'un Développeur

```python
# Tous les commits de Fil LeFebvre cette année
fil_commits = pulse_engine._get_git_pulses(
    author='Fil LeFebvre',
    since='1 year ago'
)
```

### 3. Focus sur les Fusions de Branches

```python
# Uniquement les merges des 2 dernières semaines
merge_events = pulse_engine._get_git_pulses(
    pulse_types=['merge'],
    since='2 weeks ago'
)
```

### 4. Gros Changements Structurels

```python
# Commits avec plus de 100 modifications
major_changes = pulse_engine._get_git_pulses(
    min_changes=100,
    max_changes=500,
    since='3 months ago'
)
```

### 5. Activité sur un Composant Spécifique

```python
# Commits touchant les composants de l'interface
ui_component_changes = pulse_engine._get_git_pulses(
    file_pattern='src/components',
    since='1 month ago'
)
```

### 6. Filtrage Combiné Complexe

```python
# Commits importants de Fil sur le frontend ce trimestre
significant_frontend_commits = pulse_engine._get_git_pulses(
    author='Fil LeFebvre',
    pulse_types=['commit', 'merge'],
    since='3 months ago',
    file_pattern='src/frontend',
    min_changes=50
)
```

## Conseils et Bonnes Pratiques

- Utilisez des filtres combinés pour des insights précis
- Adaptez les limites de changements à votre contexte
- Explorez différentes périodes pour comprendre l'évolution du projet

## Formats de Date Supportés

- `'1 week ago'`
- `'2023-01-01'`
- `'last month'`
- `'3 weeks ago'`

## Types de Pulses

- `'commit'`: Commits standards
- `'merge'`: Fusions de branches
- `'branch'`: Changements de branches

## Limites et Performances

- Limite par défaut : 50 pulses
- Filtrage côté Git pour performance maximale
- Gestion des erreurs intégrée