# Guide de Réponse aux Incidents de Sécurité — CyberIDE

<div align="center">

**Version 1.0.0** | Décembre 2024

*"Plan for the worst, hope for the best."*

</div>

---

## Vue d'Ensemble

Ce guide définit les procédures à suivre en cas d'incident de sécurité affectant le CyberIDE.

**Objectifs:**
- Minimiser l'impact de l'incident
- Restaurer les services rapidement
- Préserver les preuves pour l'analyse
- Respecter les obligations légales de notification

---

## Définition d'un Incident de Sécurité

Un incident de sécurité est tout événement qui:
- Compromet la **confidentialité** des données
- Compromet l'**intégrité** des données ou du système
- Compromet la **disponibilité** des services
- Viole les politiques de sécurité
- Nécessite une notification légale (Loi 25, PIPEDA, RGPD)

### Exemples d'Incidents

**CRITICAL:**
- Fuite de données personnelles (PII)
- Accès non autorisé à la base de données
- Ransomware/Malware
- Compromission de clés de chiffrement
- Prise de contrôle de serveur (RCE)

**HIGH:**
- Exploitation d'une vulnérabilité critique
- Attaque DDoS persistante
- Tentatives d'accès répétées et suspectes
- Défacement du site web
- Vol de credentials admin

**MEDIUM:**
- Spam massif
- Scan de vulnérabilités agressif
- Tentative de brute force
- Vulnérabilité découverte (non exploitée)

**LOW:**
- Vulnérabilité faible découverte
- Erreur de configuration mineure
- Faux positif de sécurité

---

## 📞 Contacts d'Urgence

### Équipe de Réponse aux Incidents (IRT)

```yaml
incident_response_team:
 lead:
 name: "Security Lead"
 email: "security@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"
 role: "Coordination générale"
 
 technical_lead:
 name: "DevSecOps Engineer"
 email: "devsecops@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"
 role: "Investigation technique"
 
 communications:
 name: "Communications Lead"
 email: "comms@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"
 role: "Communication interne/externe"

management:
 cto:
 name: "CTO"
 email: "cto@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"
 
 ceo:
 name: "CEO"
 email: "ceo@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"

legal:
 counsel:
 name: "Legal Counsel"
 email: "legal@iangelai.com"
 phone: "+1-XXX-XXX-XXXX"

external:
 cyber_insurance:
 company: "Insurance Co"
 policy: "POL-123456"
 phone: "1-800-XXX-XXXX"
 
 forensics:
 company: "Forensics Firm"
 contact: "forensics@firm.com"
 phone: "+1-XXX-XXX-XXXX"
```

### Autorités (Notification Légale)

```yaml
authorities:
 loi25_quebec:
 name: "Commission d'accès à l'information du Québec (CAI)"
 email: "caiq@caiq.qc.ca"
 phone: "1-888-528-7741"
 notification_deadline: "72 heures"
 website: "https://www.cai.gouv.qc.ca"
 
 pipeda_canada:
 name: "Commissariat à la protection de la vie privée du Canada"
 email: "info@priv.gc.ca"
 phone: "1-800-282-1376"
 notification_deadline: "dès que possible"
 website: "https://www.priv.gc.ca"
 
 gdpr_eu:
 name: "Autorité de contrôle UE (selon pays)"
 notification_deadline: "72 heures"
 website: "https://edpb.europa.eu/about-edpb/about-edpb/members_en"
```

---

## Processus de Réponse aux Incidents

### Vue d'Ensemble (PICERL)

```
┌─────────────────────────────────────────────────────────────┐
│ P: PREPARATION │
│ ├─ Documentation et procédures │
│ ├─ Formation de l'équipe │
│ ├─ Outils et accès préparés │
│ └─ Exercices réguliers (tabletop) │
├─────────────────────────────────────────────────────────────┤
│ I: IDENTIFICATION (0-30 min) │
│ ├─ Détection de l'incident │
│ ├─ Validation (vrai incident?) │
│ ├─ Classification de criticité │
│ └─ Activation de l'IRT │
├─────────────────────────────────────────────────────────────┤
│ C: CONFINEMENT (30 min - 2h) │
│ ├─ Isolation des systèmes affectés │
│ ├─ Préservation des preuves │
│ ├─ Mitigation temporaire │
│ └─ Communication initiale (interne) │
├─────────────────────────────────────────────────────────────┤
│ E: ÉRADICATION (2h - 24h) │
│ ├─ Identification cause racine │
│ ├─ Suppression de la menace │
│ ├─ Patching/Correction │
│ └─ Validation complète │
├─────────────────────────────────────────────────────────────┤
│ R: RÉCUPÉRATION (24h - 72h) │
│ ├─ Restauration des services │
│ ├─ Validation de sécurité │
│ ├─ Monitoring intensif │
│ └─ Communication de rétablissement │
├─────────────────────────────────────────────────────────────┤
│ L: LESSONS LEARNED (< 1 semaine) │
│ ├─ Post-mortem détaillé │
│ ├─ Documentation des learnings │
│ ├─ Mise à jour des procédures │
│ └─ Formation supplémentaire si nécessaire │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: IDENTIFICATION

### 1.1 Sources de Détection

| Source | Type d'Alerte | Exemple |
|--------|---------------|---------|
| **Monitoring automatisé** | SIEM, IDS/IPS | Trafic suspect, attaque détectée |
| **Scan de sécurité** | CodeQL, Snyk | Vulnérabilité critique découverte |
| **Utilisateur** | Report | Comportement anormal, phishing |
| **Chercheur en sécurité** | Responsible disclosure | Vulnérabilité signalée |
| **Autorité** | Notification | Votre système utilisé dans une attaque |

### 1.2 Validation Initiale

**Checklist:**
- [ ] Vérifier que c'est un vrai incident (pas un faux positif)
- [ ] Identifier les systèmes affectés
- [ ] Évaluer la portée initiale
- [ ] Capturer les premières preuves
- [ ] Noter l'heure de détection

**Questions clés:**
1. Quel système est affecté?
2. Quelle est la nature de l'incident?
3. Des données ont-elles été compromises?
4. L'incident est-il contenu ou actif?
5. Y a-t-il un impact utilisateur visible?

### 1.3 Classification de Criticité

**Matrice d'Impact:**

| Impact | Description | Exemple | Action |
|--------|-------------|---------|--------|
| **CRITICAL** | Compromission majeure immédiate | Fuite de PII, RCE active | Immédiate (< 15min) |
| **HIGH** | Impact significatif | Vulnérabilité critique exploitable | < 1 heure |
| **MEDIUM** | Impact modéré | Tentative d'intrusion, vulnérabilité moyenne | < 4 heures |
| **LOW** | Impact mineur | Scan de vulnérabilités, alerte mineure | < 24 heures |

### 1.4 Activation de l'Équipe

```bash
# Script d'alerte automatique
#!/bin/bash
# alert_incident.sh

SEVERITY=$1
DESCRIPTION=$2

# Slack
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
 -H 'Content-Type: application/json' \
 -d "{
 \"text\": \" SECURITY INCIDENT - ${SEVERITY}\",
 \"attachments\": [{
 \"color\": \"danger\",
 \"fields\": [{
 \"title\": \"Description\",
 \"value\": \"${DESCRIPTION}\",
 \"short\": false
 }]
 }]
 }"

# Email
python3 << EOF
import smtplib
import os
from email.message import EmailMessage

severity = os.getenv('SEVERITY', 'UNKNOWN')
description = os.getenv('DESCRIPTION', 'No description provided')
smtp_password = os.getenv('SMTP_PASSWORD')

if not smtp_password:
 print("Warning: SMTP_PASSWORD not set, skipping email")
 exit(0)

msg = EmailMessage()
msg['Subject'] = f' Security Incident - {severity}'
msg['From'] = 'security@iangelai.com'
msg['To'] = 'irt@iangelai.com'
msg.set_content(description)

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
 smtp.starttls()
 smtp.login('security@iangelai.com', smtp_password)
 smtp.send_message(msg)
EOF

# SMS (via Twilio)
# Ensure environment variables are set: TWILIO_SID, TWILIO_TOKEN
if [ -z "$TWILIO_SID" ] || [ -z "$TWILIO_TOKEN" ]; then
 echo "Warning: TWILIO_SID or TWILIO_TOKEN not set, skipping SMS"
else
 curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json \
 --data-urlencode "Body=SECURITY INCIDENT ${SEVERITY}: ${DESCRIPTION}" \
 --data-urlencode "From=+1XXX" \
 --data-urlencode "To=+1XXX" \
 -u $TWILIO_SID:$TWILIO_TOKEN
fi
```

---

## PHASE 2: CONFINEMENT

### 2.1 Confinement Immédiat (Court Terme)

**Actions selon le type d'incident:**

#### Compromission de Compte

```bash
# 1. Désactiver le compte immédiatement
python << EOF
from app.models import User
user = User.query.filter_by(email='compromised@example.com').first()
user.is_active = False
user.save()
EOF

# 2. Invalider toutes les sessions
redis-cli KEYS "session:*compromised_user_id*" | xargs redis-cli DEL

# 3. Révoquer tokens API
curl -X DELETE https://api.cyberide.com/v1/tokens/revoke \
 -H "Authorization: Bearer $ADMIN_TOKEN" \
 -d '{"user_id": "compromised_user_id"}'

# 4. Forcer reset de mot de passe
python << EOF
user.password_reset_required = True
user.password_reset_token = generate_token()
send_password_reset_email(user)
EOF
```

#### Serveur Compromis

```bash
# 1. Isoler le serveur du réseau (mais garder accès forensics)
# Sur AWS
aws ec2 modify-instance-attribute \
 --instance-id i-compromised \
 --groups sg-forensics-only

# Sur Azure
az network nsg rule create \
 --resource-group rg-cyberide \
 --nsg-name nsg-compromised \
 --name DenyAllInbound \
 --priority 100 \
 --direction Inbound \
 --access Deny

# 2. Snapshot pour analyse
aws ec2 create-snapshot \
 --volume-id vol-compromised \
 --description "Forensics snapshot - incident-$(date +%Y%m%d)"

# 3. Copier logs avant isolation complète
scp -i forensics.pem ubuntu@compromised:/var/log/* /forensics/$(date +%Y%m%d)/
```

#### Attaque DDoS

```bash
# 1. Activer protection DDoS (Cloudflare, AWS Shield)
curl -X POST https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ddos_protection \
 -H "Authorization: Bearer $CF_TOKEN" \
 -d '{"value": "on"}'

# 2. Rate limiting agressif
curl -X POST https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rate_limits \
 -H "Authorization: Bearer $CF_TOKEN" \
 -d '{
 "threshold": 10,
 "period": 60,
 "action": {
 "mode": "challenge"
 }
 }'

# 3. Bloquer IPs suspectes
cat suspicious_ips.txt | while read ip; do
 iptables -A INPUT -s $ip -j DROP
done
```

### 2.2 Préservation des Preuves

```bash
# 1. Capturer état système
mkdir -p /forensics/$(date +%Y%m%d-%H%M%S)
cd /forensics/$(date +%Y%m%d-%H%M%S)

# Processus actifs
ps auxf > processes.txt

# Connexions réseau
netstat -anp > network_connections.txt
ss -anp > socket_stats.txt

# Utilisateurs connectés
w > users_logged_in.txt

# Logs système
tar -czf system_logs.tar.gz /var/log/

# Historique commandes
cat ~/.bash_history > bash_history.txt

# 2. Dump mémoire RAM (si possible)
sudo apt-get install volatility3
sudo python3 vol.py -f /proc/kcore linux.pslist > memory_processes.txt

# 3. Capturer trafic réseau
tcpdump -i any -w capture.pcap &
TCPDUMP_PID=$!
sleep 300 # 5 minutes
kill $TCPDUMP_PID

# 4. Calculer checksums (intégrité)
find /forensics -type f -exec sha256sum {} \; > checksums.txt
```

### 2.3 Communication Interne

**Template Email - Alerte Interne:**

```
TO: team@iangelai.com
FROM: security@iangelai.com
SUBJECT: [URGENT] Security Incident - Action Required

Team,

We are currently responding to a security incident:

SEVERITY: [CRITICAL/HIGH/MEDIUM/LOW]
TYPE: [Description]
DETECTED: [Timestamp]
AFFECTED SYSTEMS: [List]

IMMEDIATE ACTIONS REQUIRED:
- [Action 1]
- [Action 2]

DO NOT:
- Discuss externally
- Post on social media
- Delete any logs or data

UPDATES:
We will provide updates every [X] hours or as situation evolves.

Contact security@iangelai.com for questions.

Security Team
```

---

## PHASE 3: ÉRADICATION

### 3.1 Analyse de Cause Racine

**Méthodologie "5 Whys":**

```
Incident: Fuite de données via API

Why 1: Pourquoi y a-t-il eu fuite?
→ API endpoint n'avait pas d'authentification

Why 2: Pourquoi pas d'authentification?
→ Code review n'a pas détecté le problème

Why 3: Pourquoi code review n'a pas détecté?
→ Checklist de sécurité n'incluait pas ce point

Why 4: Pourquoi checklist incomplète?
→ Pas de mise à jour après changement d'architecture

Why 5: Pourquoi pas de mise à jour?
→ Pas de processus de révision de sécurité

CAUSE RACINE: Manque de processus de révision régulière des contrôles de sécurité
```

### 3.2 Suppression de la Menace

#### Malware/Backdoor

```bash
# 1. Identifier fichiers malveillants
sudo find / -name "*.php.suspected" -o -name "*.jsp.backdoor"

# 2. Vérifier intégrité avec AIDE
sudo aide --check

# 3. Scanner avec ClamAV
sudo clamscan -r -i --remove /var/www/

# 4. Nettoyer cron jobs malveillants
sudo crontab -l -u www-data
sudo crontab -r -u www-data

# 5. Vérifier modifications non autorisées
sudo debsums -c # Debian/Ubuntu
sudo rpm -Va # RedHat/CentOS
```

#### Vulnérabilité Applicative

```bash
# 1. Déployer patch en urgence
git pull origin security-patch-CVE-2024-XXXXX
npm install
npm run build
sudo systemctl restart cyberide-backend

# 2. Vérifier que patch est appliqué
curl https://api.cyberide.com/health/security-version
# Devrait retourner version patchée

# 3. Rescanner avec CodeQL
gh api /repos/iAngelAi/iAngel-CyberIDE/code-scanning/analyses \
 --jq '.[] | select(.tool.name=="CodeQL") | {id, created_at, state}'
```

### 3.3 Renforcement de Sécurité

```yaml
# checklist_post_incident.yml
hardening:
 - name: "Rotation Secrets"
 actions:
 - Rotate all API keys
 - Rotate database passwords
 - Rotate JWT secrets
 - Update .env.example

 - name: "Access Control Review"
 actions:
 - Review all user permissions
 - Remove unused accounts
 - Enforce MFA for all admins
 - Review RBAC policies

 - name: "Network Segmentation"
 actions:
 - Update firewall rules
 - Restrict database access
 - Review security groups (AWS)
 - Update network ACLs

 - name: "Monitoring Enhancement"
 actions:
 - Add alerts for similar patterns
 - Increase log verbosity
 - Enable audit logging
 - Configure SIEM rules
```

---

## PHASE 4: RÉCUPÉRATION

### 4.1 Restauration Sécurisée

```bash
# 1. Vérifier intégrité des backups
sha256sum backup-20241208.tar.gz
# Comparer avec checksum connu

# 2. Restaurer depuis backup vérifié
tar -xzf backup-20241208.tar.gz
docker-compose down
docker-compose up -d

# 3. Valider fonctionnement
curl https://api.cyberide.com/health
npm run test:e2e

# 4. Monitoring intensif post-restauration
# Vérifier logs toutes les 15 minutes pendant 24h
watch -n 900 'tail -100 /var/log/cyberide/app.log | grep -i error'
```

### 4.2 Tests de Validation

**Checklist:**
- [ ] Tous les services sont opérationnels
- [ ] Tests de sécurité passent (SAST, DAST)
- [ ] Pas d'activité suspecte dans les logs
- [ ] Monitoring fonctionne correctement
- [ ] Backups fonctionnent
- [ ] Alertes configurées correctement

### 4.3 Communication de Rétablissement

**Template - Service Restored:**

```
TO: affected_users@iangelai.com
FROM: security@iangelai.com
SUBJECT: Service Restored - Security Incident Update

Dear CyberIDE Users,

Following the security incident reported on [DATE], we are pleased to inform you that:

 The incident has been fully resolved
 All services are now operational
 Enhanced security measures are in place

WHAT HAPPENED:
[Brief, transparent explanation]

WHAT WE DID:
[Actions taken to resolve and prevent]

WHAT YOU SHOULD DO:
- [Action 1, e.g., change password]
- [Action 2, e.g., review recent activity]

For questions: security@iangelai.com

Thank you for your patience.

CyberIDE Security Team
```

---

## PHASE 5: LESSONS LEARNED

### 5.1 Post-Mortem Template

```markdown
# Security Incident Post-Mortem

## Incident Summary
- **Date/Time:** 2024-12-08 14:30 UTC
- **Duration:** 4 hours 15 minutes
- **Severity:** HIGH
- **Impact:** User data temporarily inaccessible

## Timeline
| Time | Event |
|------|-------|
| 14:30 | Incident detected by monitoring |
| 14:35 | IRT activated |
| 14:50 | Affected systems isolated |
| 16:00 | Cause identified |
| 17:30 | Patch deployed |
| 18:45 | Services fully restored |

## Root Cause
[Detailed technical explanation]

## What Went Well
- Fast detection (5 minutes)
- Effective communication
- Good documentation

## What Didn't Go Well
- Delayed isolation (20 minutes)
- Missing runbook for this scenario
- Unclear escalation path

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Update firewall rules | DevOps | 2024-12-15 | 🟡 In Progress |
| Create runbook | Security | 2024-12-10 | 🟢 Done |
| Additional monitoring | SRE | 2024-12-20 | 🔴 Todo |

## Metrics
- **MTTD** (Mean Time To Detect): 5 minutes
- **MTTR** (Mean Time To Remediate): 4h 15m
- **Impact:** 150 users, no data loss

## Follow-up
- Post-mortem review meeting: 2024-12-10
- Update incident response plan: 2024-12-15
- Team training session: 2024-12-22
```

### 5.2 Mise à Jour des Procédures

```bash
# Script pour vérifier que procédures sont à jour
#!/bin/bash
# check_procedures.sh

DOCS_DIR="/docs/security"
MAX_AGE_DAYS=90

find $DOCS_DIR -name "*.md" -type f | while read file; do
 LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d" "$file")
 AGE_DAYS=$(( ($(date +%s) - $(date -j -f "%Y-%m-%d" "$LAST_MODIFIED" +%s)) / 86400 ))
 
 if [ $AGE_DAYS -gt $MAX_AGE_DAYS ]; then
 echo " $file not updated in $AGE_DAYS days (> $MAX_AGE_DAYS)"
 else
 echo " $file up to date"
 fi
done
```

---

## Métriques et KPIs

### Métriques de Performance

| Métrique | Objectif | Actuel | Status |
|----------|----------|--------|--------|
| MTTD (Mean Time To Detect) | < 15 min | 8 min | |
| MTTR (Mean Time To Remediate) | < 4h | 3.5h | |
| Incidents critiques par mois | 0 | 0 | |
| Faux positifs | < 10% | 12% | |
| Couverture runbooks | 100% | 85% | |

### Reporting

```python
# Génération rapport mensuel
from jinja2 import Template

template = Template("""
# Security Incident Report - {{ month }} {{ year }}

## Summary
- Total Incidents: {{ total }}
- Critical: {{ critical }}
- High: {{ high }}
- Medium: {{ medium }}
- Low: {{ low }}

## Top Incident Types
{% for type, count in top_types %}
- {{ type }}: {{ count }}
{% endfor %}

## Average Response Times
- MTTD: {{ mttd }} minutes
- MTTR: {{ mttr }} hours

## Trends
{{ trends_chart }}
""")

report = template.render(
 month="December",
 year="2024",
 total=5,
 critical=0,
 high=1,
 medium=2,
 low=2,
 top_types=[("Phishing", 2), ("Vuln Scan", 2), ("DDoS", 1)],
 mttd=8,
 mttr=3.5,
 trends_chart="[Chart data]"
)

print(report)
```

---

## Ressources

### Runbooks Détaillés

- [DDoS Attack Response](./runbooks/ddos.md)
- [Data Breach Response](./runbooks/data_breach.md)
- [Ransomware Response](./runbooks/ransomware.md)
- [Account Compromise](./runbooks/account_compromise.md)

### Templates

- [Incident Ticket Template](./templates/incident_ticket.md)
- [Communication Template](./templates/communication.md)
- [Post-Mortem Template](./templates/postmortem.md)

### Training

- [Incident Response Training](./training/ir_training.md)
- [Tabletop Exercises](./training/tabletop.md)

---

<div align="center">

** Prepared, Not Scared **

*"It's not if, it's when. Be ready."*

</div>
