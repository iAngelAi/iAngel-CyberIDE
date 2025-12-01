# **🗺 Roadmap: Project Neural Core**

Cette roadmap détaille l'évolution du simple IDE vers le "Moniteur Neuronal Complet".

## **Phase 1 : L'Interface & Le Moteur 3D (✅ Actuel)**

* \[x\] Création de l'interface React "Cyberpunk".  
* \[x\] Intégration initiale Three.js / Canvas pour le fond animé.  
* \[x\] Mockup des états d'erreurs (Glitch effects).  
* \[x\] Système de fichiers virtuel.

## **Phase 2 : Le "Backend Bridge" & Analyseur Local (🚧 En cours)**

*L'objectif est de lier l'état réel des fichiers locaux à l'animation 3D.*

* \[ \] **Développement du CLI Python (neural\_cli)** :  
  * Script qui scanne le dossier /src et /tests.  
  * Détection de la présence de LICENSE, README.md, requirements.txt.  
* \[ \] **Système de "Status File"** :  
  * Le CLI génère un fichier neural\_status.json en temps réel.  
  * Le Frontend lit ce fichier pour ajuster l'intensité du cerveau (0.0 à 1.0).  
* \[ \] **Intégration des Tests Unitaires** :  
  * Hook automatique : Quand pytest ou npm test échoue \-\> Mise à jour du JSON \-\> Le Cerveau vire au rouge.

## **Phase 3 : "The Soul" \- Paramètres & Génération (✨ Geek Feature)**

*Donner le contrôle total à l'utilisateur via l'UI.*

* \[ \] **Panneau de Configuration Avancé** :  
  * Formulaire : "Stack Techno", "Type de Licence", "Fournisseur API".  
  * Action : Bouton "Auto-Generate" qui demande à l'IA de créer les fichiers réels basés sur ces choix.  
* \[ \] **Initialisation du LLM** :  
  * Injection automatique du contexte projet dans le prompt système de l'IA via .claude/rules.

## **Phase 4 : Production Uplink (🚀 Final)**

* \[ \] **Mode "Satellite"** :  
  * Animation spéciale quand Coverage \> 90% et Git Clean.  
* \[ \] **Intégration MCP (Model Context Protocol)** :  
  * Connecter directement le Neural Core aux APIs de Claude/OpenAI pour une conscience contextuelle totale.

## **Métriques de Réussite (Neural Illumination)**

| Niveau | Critères | Effet Visuel |
| :---- | :---- | :---- |
| **0%** | Projet vide | Noir complet, légers bruits de fond |
| **25%** | Structure de base \+ Config | Faible lueur bleue au centre (Tronc cérébral) |
| **50%** | Logique métier \+ Modules | Lobes illuminés, connexions synaptiques lentes |
| **75%** | Tests passés \+ Docs | Pulsations rapides, couleur Cyan/Magenta |
| **100%** | Prod Ready \+ Sécurité | **FULL UPLINK** (Blanc éclatant / Or) |
| **ERR** | Test Failed / Regression | **ZONE ROUGE** \+ Diagnostic Textuel |

