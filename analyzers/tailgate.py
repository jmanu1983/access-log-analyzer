"""
Tailgate Analyzer — Detect potential tailgating / piggybacking events.

Identifies cases where two different badges are used at the same access point
within a very short time window, which may indicate one person following
another through a door without presenting their own credential.
"""

import pandas as pd


class TailgateAnalyzer:
    """Detect potential tailgating events from access logs."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def detect_rapid_follows(self, max_seconds: int = 3) -> pd.DataFrame:
        """
        Find events where two different persons used the same access point
        within `max_seconds` of each other.

        Args:
            max_seconds: Maximum time gap in seconds to flag as tailgating.

        Returns:
            DataFrame with columns: EventTime, AccessPoint, Person1, Person2,
            GapSeconds.
        """
        # Filter to granted events only
        granted = self.df[self.df["Granted"] == True].copy()
        granted = granted.sort_values(["AccessPointName", "EventTime"])

        results = []

        for ap_name, group in granted.groupby("AccessPointName"):
            if len(group) < 2:
                continue

            times = group["EventTime"].values
            pnrs = group["PersonnelNr"].values
            names = (group["LastName"].fillna("") + ", " + group["FirstName"].fillna("")).values

            for i in range(1, len(times)):
                gap = (times[i] - times[i - 1]) / pd.Timedelta(seconds=1)
                if 0 < gap <= max_seconds and pnrs[i] != pnrs[i - 1]:
                    results.append({
                        "EventTime": pd.Timestamp(times[i]),
                        "AccessPoint": ap_name,
                        "Person1": f"{pnrs[i-1]} ({names[i-1]})",
                        "Person2": f"{pnrs[i]} ({names[i]})",
                        "GapSeconds": round(gap, 1),
                    })

        return pd.DataFrame(results)
