"""
Report Generator — Output analysis results as HTML and CSV files.
"""

import os
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate HTML and CSV reports from analysis results."""

    def __init__(self, output_dir: str = "reports", timestamp: str = None):
        self.output_dir = output_dir
        self.ts = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

    def to_csv(self, results: dict) -> None:
        """Export all DataFrames in results to CSV files."""
        for key, value in results.items():
            if isinstance(value, pd.DataFrame) and not value.empty:
                path = os.path.join(self.output_dir, f"{key}_{self.ts}.csv")
                value.to_csv(path, index=False)
                logger.info("CSV: %s (%d rows)", path, len(value))

    def to_html(self, results: dict) -> None:
        """Generate a styled HTML report."""
        path = os.path.join(self.output_dir, f"report_{self.ts}.html")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Access Log Analysis Report — {self.ts}</title>
<style>
    :root {{ --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a;
             --text: #e4e6eb; --accent: #3b82f6; --success: #22c55e;
             --danger: #ef4444; --warning: #f59e0b; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--bg);
            color: var(--text); padding: 32px; line-height: 1.6; }}
    h1 {{ color: var(--accent); margin-bottom: 8px; }}
    h2 {{ color: var(--text); margin: 32px 0 16px; font-size: 1.2rem; }}
    .meta {{ color: #8b8fa3; margin-bottom: 32px; }}
    .kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px; margin-bottom: 32px; }}
    .kpi {{ background: var(--surface); border: 1px solid var(--border);
            border-radius: 12px; padding: 20px; text-align: center; }}
    .kpi-value {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
    .kpi-label {{ font-size: 0.85rem; color: #8b8fa3; margin-top: 4px; }}
    .kpi.alert .kpi-value {{ color: var(--danger); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem;
             background: var(--surface); border-radius: 8px; overflow: hidden; }}
    th {{ background: var(--border); padding: 10px 12px; text-align: left; }}
    td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); }}
    tr:hover {{ background: rgba(59, 130, 246, 0.05); }}
    .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px;
              font-size: 0.75rem; font-weight: 600; }}
    .badge.spike {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); }}
    .badge.drop {{ background: rgba(59, 130, 246, 0.15); color: var(--accent); }}
</style>
</head>
<body>
<h1>Access Log Analysis Report</h1>
<p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
   Period: {results.get('period_days', '?')} days |
   Total events: {results.get('total_events', 0):,}</p>

<div class="kpi-row">
    <div class="kpi">
        <div class="kpi-value">{results.get('total_events', 0):,}</div>
        <div class="kpi-label">Total Events</div>
    </div>
    <div class="kpi">
        <div class="kpi-value">{results.get('grant_rate', {{}}).get('grant_rate_pct', 0)}%</div>
        <div class="kpi-label">Grant Rate</div>
    </div>
    <div class="kpi">
        <div class="kpi-value">{results.get('grant_rate', {{}}).get('denied', 0):,}</div>
        <div class="kpi-label">Denied Events</div>
    </div>
    <div class="kpi alert">
        <div class="kpi-value">{len(results.get('rapid_follows', []))}</div>
        <div class="kpi-label">Tailgating Alerts</div>
    </div>
</div>
"""

        # Top access points
        top_doors = results.get("top_doors")
        if isinstance(top_doors, pd.DataFrame) and not top_doors.empty:
            html += "<h2>Top Access Points</h2>\n"
            html += top_doors.to_html(index=False, classes="", border=0)

        # Top users
        top_users = results.get("top_users")
        if isinstance(top_users, pd.DataFrame) and not top_users.empty:
            html += "<h2>Most Active Users</h2>\n"
            html += top_users.head(15).to_html(index=False, classes="", border=0)

        # Hourly anomalies
        anomalies = results.get("hourly_anomalies")
        if isinstance(anomalies, pd.DataFrame) and not anomalies.empty:
            html += f"<h2>Hourly Anomalies ({len(anomalies)} detected)</h2>\n"
            html += anomalies.to_html(index=False, classes="", border=0)

        # User anomalies
        user_anom = results.get("user_anomalies")
        if isinstance(user_anom, pd.DataFrame) and not user_anom.empty:
            html += f"<h2>User Activity Anomalies ({len(user_anom)} detected)</h2>\n"
            html += user_anom.head(20).to_html(index=False, classes="", border=0)

        # Tailgating
        rapid = results.get("rapid_follows")
        if isinstance(rapid, pd.DataFrame) and not rapid.empty:
            html += f"<h2>Potential Tailgating ({len(rapid)} events)</h2>\n"
            html += rapid.head(30).to_html(index=False, classes="", border=0)

        html += "\n</body>\n</html>"

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("HTML report: %s", path)
