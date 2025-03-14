# Analyseur de logs d'accès AEOS

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-CC2927?logo=microsoftsqlserver&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Outil d'**analyse de sécurité** qui se connecte à la base SQL Server Nedap AEOS via la vue `vw_AeosEventLog`, extrait les événements d'accès et produit des informations exploitables : schémas de trafic, détection d'anomalies statistiques, alertes de tailgating, et rapports HTML/CSV stylés.

## Modèle de données AEOS

Toutes les requêtes et colonnes utilisent les noms de champs définis dans le **WSDL AEOS** (`EventInfo`) :

| Colonne | Type | Description |
|---------|------|-------------|
| `DateTime` | datetime | Horodatage de l'événement |
| `EventTypeName` | string | "Access granted", "Access denied: badge blocked", "Door forced open"… |
| `AccesspointId` | long | ID du point d'accès |
| `AccesspointName` | string | Nom du point d'accès |
| `EntranceName` | string | Nom de l'entrée |
| `CarrierId` | long | ID du porteur AEOS |
| `CarrierFullName` | string | Nom complet du porteur |
| `Identifier` | string | Numéro de badge |
| `HostName` | string | Nom du contrôleur |

> **Note :** Le champ `Granted` (booléen) est dérivé de `EventTypeName` — il n'existe pas nativement dans AEOS. "Access granted*" → `True`, "Access denied*" → `False`.

## Modules d'analyse

### 1. Analyse de trafic
- Distribution horaire des événements (Access granted vs Access denied)
- Tendance quotidienne sur la période d'analyse
- Top-N des `AccesspointName` les plus fréquentés
- Top-N des porteurs (`CarrierFullName` / `Identifier`) les plus actifs
- Ratio global accordés/refusés

### 2. Détection d'anomalies (Z-Score)
- **Anomalies de volume horaire** — Pics ou chutes du nombre d'événements par heure
- **Anomalies d'activité utilisateur** — Individus (`CarrierId`) avec une utilisation quotidienne anormalement élevée
- **Accès hors horaires** — Événements en dehors des heures ouvrables (07h00–20h00) et les week-ends

### 3. Détection de tailgating
- Identifie les événements de suivi rapide : deux `CarrierId` différents au même `AccesspointName` en quelques secondes
- Ne considère que les événements "Access granted" (les événements refusés n'ouvrent pas la porte)
- Seuil de temps configurable (défaut : 3 secondes)

### 4. Génération de rapports
- **Rapport HTML** — Rapport stylé avec thème sombre, cartes KPI et tableaux
- **Export CSV** — Données lisibles par machine pour chaque module d'analyse

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Langage | Python 3.10+ |
| Données | Pandas, NumPy |
| Base de données | SQL Server (pyodbc) — vue `vw_AeosEventLog` |
| Sortie | HTML + CSS, CSV |

## Installation

```bash
git clone https://github.com/jmanu1983/access-log-analyzer.git
cd access-log-analyzer

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

Modifier `.env` avec vos paramètres de connexion SQL Server AEOS.

## Prérequis SQL Server

L'analyseur interroge la vue `vw_AeosEventLog` qui doit être créée par le DBA pour exposer le journal d'événements AEOS avec des colonnes alignées sur le WSDL :

```sql
CREATE VIEW dbo.vw_AeosEventLog AS
SELECT
    e.Id,
    e.EventTypeId,
    et.Name            AS EventTypeName,
    e.EventDateTime    AS [DateTime],
    e.HostName,
    e.AccesspointId,
    ap.Name            AS AccesspointName,
    e.EntranceId,
    en.Name            AS EntranceName,
    e.IdentifierId,
    i.Code             AS Identifier,
    e.CarrierId,
    e.CarrierFullName
FROM dbo.<table_evenements_interne> e
LEFT JOIN dbo.<table_types_evenements> et ON e.EventTypeId = et.Id
LEFT JOIN dbo.<table_access_points> ap   ON e.AccesspointId = ap.Id
LEFT JOIN dbo.<table_entrances> en       ON e.EntranceId = en.Id
LEFT JOIN dbo.<table_identifiers> i      ON e.IdentifierId = i.Id;
```

> Les noms de tables internes AEOS varient selon la version. Consultez votre DBA pour les noms exacts. Accès en lecture seule uniquement.

## Utilisation

```bash
# Analyser les 30 derniers jours, sortie HTML + CSV
python main.py --days 30

# Analyser les 7 derniers jours, HTML uniquement, seuil d'anomalie plus strict
python main.py --days 7 --format html --threshold 1.5

# Répertoire de sortie personnalisé
python main.py --days 90 --output ./mes-rapports
```

### Options de la ligne de commande

| Option | Défaut | Description |
|--------|--------|-------------|
| `--days` | 30 | Nombre de jours à analyser |
| `--output` | `reports/` | Répertoire de sortie |
| `--format` | `both` | `html`, `csv`, ou `both` |
| `--threshold` | 2.0 | Seuil Z-score pour la détection d'anomalies |

## Structure du projet

```
access-log-analyzer/
├── main.py                     # Point d'entrée CLI
├── analyzers/
│   ├── data_loader.py          # Extraction via vw_AeosEventLog (pyodbc)
│   ├── traffic.py              # Analyse de schémas de trafic
│   ├── anomaly.py              # Détection d'anomalies Z-score
│   ├── tailgate.py             # Détection de tailgating
│   └── report_generator.py     # Sortie rapports HTML + CSV
├── reports/                    # Rapports générés (hors VCS)
├── .env.example
├── requirements.txt
└── README.md
```

## Licence

Ce projet est sous licence MIT.
