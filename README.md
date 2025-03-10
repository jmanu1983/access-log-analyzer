# Analyseur de logs d'accès

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-CC2927?logo=microsoftsqlserver&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Outil d'**analyse de sécurité** qui se connecte à la base SQL Server Nedap AEOS, extrait les événements d'accès et produit des informations exploitables : schémas de trafic, détection d'anomalies statistiques, alertes de tailgating, et rapports HTML/CSV stylés.

## Modules d'analyse

### 1. Analyse de trafic
- Distribution horaire des événements (accordés vs refusés)
- Tendance quotidienne sur la période d'analyse
- Top-N des points d'accès les plus fréquentés
- Top-N des porteurs de badges les plus actifs
- Ratio global accordés/refusés

### 2. Détection d'anomalies (Z-Score)
- **Anomalies de volume horaire** — Pics ou chutes du nombre d'événements par heure
- **Anomalies d'activité utilisateur** — Individus avec une utilisation quotidienne anormalement élevée
- **Accès hors horaires** — Événements en dehors des heures ouvrables (07h00–20h00) et les week-ends

### 3. Détection de tailgating
- Identifie les événements de suivi rapide : deux badges différents au même point d'accès en quelques secondes
- Seuil de temps configurable (défaut : 3 secondes)

### 4. Génération de rapports
- **Rapport HTML** — Rapport stylé avec thème sombre, cartes KPI et tableaux
- **Export CSV** — Données lisibles par machine pour chaque module d'analyse

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Langage | Python 3.10+ |
| Données | Pandas, NumPy |
| Base de données | SQL Server (pyodbc) |
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

## Exemple de sortie

Le rapport HTML inclut :
- **Cartes KPI** — Événements totaux, taux d'accès, refusés, alertes tailgating
- **Top points d'accès** — Classement par volume d'événements
- **Utilisateurs les plus actifs** — Porteurs de badges avec l'utilisation la plus élevée
- **Anomalies horaires** — Périodes avec activité statistiquement inhabituelle
- **Anomalies utilisateur** — Individus avec comportement atypique
- **Événements de tailgating** — Présentations de badges en suivi rapide

## Structure du projet

```
access-log-analyzer/
├── main.py                     # Point d'entrée CLI
├── analyzers/
│   ├── data_loader.py          # Extraction SQL Server
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
