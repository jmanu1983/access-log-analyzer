"""
Tailgate Analyzer — Detect potential tailgating / piggybacking events.

Identifies cases where two different carriers (AEOS CarrierId) are recorded
at the same access point (AccesspointName) within a very short time window,
which may indicate one person following another through a door without
presenting their own credential.

Column names follow the AEOS WSDL EventInfo schema:
    DateTime, EventTypeName, AccesspointName, CarrierId, CarrierFullName, Identifier
"""

import pandas as pd


class TailgateAnalyzer:
    """Detect potential tailgating events from AEOS access logs."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def detect_rapid_follows(self, max_seconds: int = 3) -> pd.DataFrame:
        """
        Find events where two different carriers used the same access point
        within `max_seconds` of each other.

        Only considers "Access granted" events (EventTypeName starting with
        'Access granted'), since denied events don't open the door.

        Args:
            max_seconds: Maximum time gap in seconds to flag as tailgating.

        Returns:
            DataFrame with columns: DateTime, AccesspointName, Carrier1,
            Carrier2, GapSeconds.
        """
        # Filter to granted events only (AEOS EventTypeName pattern)
        granted = self.df[
            self.df["EventTypeName"].str.lower().str.startswith("access granted", na=False)
        ].copy()
        granted = granted.sort_values(["AccesspointName", "DateTime"])

        results = []

        for ap_name, group in granted.groupby("AccesspointName"):
            if len(group) < 2:
                continue

            times = group["DateTime"].values
            carrier_ids = group["CarrierId"].values
            names = group["CarrierFullName"].fillna("").values
            identifiers = group["Identifier"].fillna("").values

            for i in range(1, len(times)):
                gap = (times[i] - times[i - 1]) / pd.Timedelta(seconds=1)
                if 0 < gap <= max_seconds and carrier_ids[i] != carrier_ids[i - 1]:
                    results.append({
                        "DateTime": pd.Timestamp(times[i]),
                        "AccesspointName": ap_name,
                        "Carrier1": f"{names[i-1]} [{identifiers[i-1]}]",
                        "Carrier2": f"{names[i]} [{identifiers[i]}]",
                        "GapSeconds": round(gap, 1),
                    })

        return pd.DataFrame(results)
