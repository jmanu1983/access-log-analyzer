"""
Traffic Analyzer — Patterns and distributions in access events.
"""

import pandas as pd


class TrafficAnalyzer:
    """Analyze traffic patterns from access event data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def hourly_distribution(self) -> pd.DataFrame:
        """Events grouped by hour of day."""
        grouped = self.df.groupby("Hour").agg(
            total=("Granted", "count"),
            granted=("Granted", "sum"),
        ).reset_index()
        grouped["denied"] = grouped["total"] - grouped["granted"]
        grouped["grant_rate"] = (grouped["granted"] / grouped["total"] * 100).round(1)
        return grouped

    def daily_trend(self) -> pd.DataFrame:
        """Events grouped by date."""
        grouped = self.df.groupby("Date").agg(
            total=("Granted", "count"),
            granted=("Granted", "sum"),
        ).reset_index()
        grouped["denied"] = grouped["total"] - grouped["granted"]
        return grouped.sort_values("Date")

    def top_access_points(self, n: int = 10) -> pd.DataFrame:
        """Most active access points."""
        return (
            self.df.groupby("AccessPointName")
            .agg(total=("Granted", "count"), granted=("Granted", "sum"))
            .reset_index()
            .assign(denied=lambda x: x["total"] - x["granted"])
            .sort_values("total", ascending=False)
            .head(n)
        )

    def top_users(self, n: int = 20) -> pd.DataFrame:
        """Most active badge holders."""
        return (
            self.df.groupby(["PersonnelNr", "LastName", "FirstName", "Company"])
            .agg(total=("Granted", "count"), denied=("Granted", lambda x: (~x.astype(bool)).sum()))
            .reset_index()
            .sort_values("total", ascending=False)
            .head(n)
        )

    def grant_deny_ratio(self) -> dict:
        """Overall granted vs denied ratio."""
        total = len(self.df)
        granted = int(self.df["Granted"].sum())
        denied = total - granted
        return {
            "total": total,
            "granted": granted,
            "denied": denied,
            "grant_rate_pct": round(granted / total * 100, 2) if total else 0,
        }
