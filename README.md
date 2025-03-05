# Access Log Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-CC2927?logo=microsoftsqlserver&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A **security analytics tool** that connects to the Nedap AEOS SQL Server database, extracts access events, and produces actionable intelligence: traffic patterns, statistical anomaly detection, tailgating alerts, and styled HTML/CSV reports.

## Analysis Modules

### 1. Traffic Analysis
- Hourly event distribution (granted vs. denied)
- Daily trend over the analysis period
- Top-N busiest access points
- Top-N most active badge holders
- Overall grant/deny ratio

### 2. Anomaly Detection (Z-Score)
- **Hourly volume anomalies** — Spikes or drops in event count per hour
- **User activity anomalies** — Individuals with unusually high daily usage
- **Off-hours access** — Events outside business hours (07:00–20:00) and weekends

### 3. Tailgating Detection
- Identifies rapid-follow events: two different badges at the same door within N seconds
- Configurable time threshold (default: 3 seconds)

### 4. Report Generation
- **HTML report** — Dark-themed, styled report with KPI cards and tables
- **CSV export** — Machine-readable data for each analysis module

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Data | Pandas, NumPy |
| Database | SQL Server (pyodbc) |
| Output | HTML + CSS, CSV |

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

Edit `.env` with your AEOS SQL Server connection details.

## Usage

```bash
# Analyze last 30 days, output HTML + CSV
python main.py --days 30

# Analyze last 7 days, HTML only, stricter anomaly threshold
python main.py --days 7 --format html --threshold 1.5

# Custom output directory
python main.py --days 90 --output ./my-reports
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--days` | 30 | Number of days to analyze |
| `--output` | `reports/` | Output directory |
| `--format` | `both` | `html`, `csv`, or `both` |
| `--threshold` | 2.0 | Z-score threshold for anomaly detection |

## Sample Output

The HTML report includes:
- **KPI cards** — Total events, grant rate, denied count, tailgating alerts
- **Top access points** — Ranked by event volume
- **Most active users** — Badge holders with highest usage
- **Hourly anomalies** — Time periods with statistically unusual activity
- **User anomalies** — Individuals with outlier behavior
- **Tailgating events** — Rapid-follow badge presentations

## Project Structure

```
access-log-analyzer/
├── main.py                     # CLI entry point
├── analyzers/
│   ├── data_loader.py          # SQL Server data extraction
│   ├── traffic.py              # Traffic pattern analysis
│   ├── anomaly.py              # Z-score anomaly detection
│   ├── tailgate.py             # Tailgating detection
│   └── report_generator.py     # HTML + CSV report output
├── reports/                    # Generated reports (gitignored)
├── .env.example
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License.
