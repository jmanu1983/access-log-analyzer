"""
Access Log Analyzer — Main CLI entry point

Connects to the AEOS SQL Server database, extracts access events, and runs
a suite of security analytics: traffic patterns, anomaly detection,
tailgating analysis, and generates HTML/CSV reports.

Usage:
    python main.py --days 30 --output reports/
    python main.py --days 7 --format html
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from analyzers.data_loader import load_events
from analyzers.traffic import TrafficAnalyzer
from analyzers.anomaly import AnomalyDetector
from analyzers.tailgate import TailgateAnalyzer
from analyzers.report_generator import ReportGenerator

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("access-log-analyzer")


def main():
    parser = argparse.ArgumentParser(
        description="AEOS Access Log Analyzer — Security analytics and anomaly detection"
    )
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    parser.add_argument("--output", default="reports", help="Output directory for reports (default: reports/)")
    parser.add_argument("--format", choices=["html", "csv", "both"], default="both", help="Report format")
    parser.add_argument("--threshold", type=float, default=2.0, help="Anomaly detection Z-score threshold (default: 2.0)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info("=== AEOS Access Log Analyzer ===")
    logger.info("Period: last %d days", args.days)
    logger.info("Output: %s", args.output)

    # 1. Load data from SQL Server
    logger.info("Loading access events from SQL Server...")
    df = load_events(days=args.days)
    logger.info("Loaded %d events", len(df))

    if df.empty:
        logger.warning("No events found. Exiting.")
        sys.exit(0)

    # 2. Traffic analysis
    logger.info("Running traffic analysis...")
    traffic = TrafficAnalyzer(df)
    hourly_stats = traffic.hourly_distribution()
    daily_stats = traffic.daily_trend()
    top_doors = traffic.top_access_points(n=15)
    top_users = traffic.top_users(n=20)
    grant_rate = traffic.grant_deny_ratio()

    # 3. Anomaly detection
    logger.info("Running anomaly detection (threshold=%.1f)...", args.threshold)
    detector = AnomalyDetector(df, z_threshold=args.threshold)
    hourly_anomalies = detector.detect_hourly_anomalies()
    user_anomalies = detector.detect_user_anomalies()
    off_hours = detector.detect_off_hours_access()
    logger.info("Found %d hourly anomalies, %d user anomalies, %d off-hours events",
                len(hourly_anomalies), len(user_anomalies), len(off_hours))

    # 4. Tailgate / rapid follow analysis
    logger.info("Running tailgate analysis...")
    tailgate = TailgateAnalyzer(df)
    rapid_follows = tailgate.detect_rapid_follows(max_seconds=3)
    logger.info("Found %d potential tailgating events", len(rapid_follows))

    # 5. Generate reports
    logger.info("Generating reports...")
    generator = ReportGenerator(output_dir=args.output, timestamp=timestamp)

    results = {
        "period_days": args.days,
        "total_events": len(df),
        "hourly_stats": hourly_stats,
        "daily_stats": daily_stats,
        "top_doors": top_doors,
        "top_users": top_users,
        "grant_rate": grant_rate,
        "hourly_anomalies": hourly_anomalies,
        "user_anomalies": user_anomalies,
        "off_hours_access": off_hours,
        "rapid_follows": rapid_follows,
    }

    if args.format in ("csv", "both"):
        generator.to_csv(results)

    if args.format in ("html", "both"):
        generator.to_html(results)

    logger.info("=== Analysis complete ===")


if __name__ == "__main__":
    main()
