"""
Anomaly Detector — Statistical anomaly detection for access events.

Uses Z-score analysis to identify unusual patterns in:
- Hourly event volumes (spikes or drops)
- Individual user activity (unusual badge usage)
- Off-hours access (events outside business hours)
"""

import pandas as pd
import numpy as np


class AnomalyDetector:
    """Detect anomalies in access event data using statistical methods."""

    def __init__(self, df: pd.DataFrame, z_threshold: float = 2.0):
        self.df = df
        self.z_threshold = z_threshold

    def detect_hourly_anomalies(self) -> pd.DataFrame:
        """
        Find hours with unusually high or low event counts.

        Groups events by date+hour, computes Z-scores, and flags
        any hour that deviates more than `z_threshold` standard deviations.
        """
        hourly = (
            self.df.groupby([self.df["EventTime"].dt.date, "Hour"])
            .size()
            .reset_index(name="count")
        )
        hourly.columns = ["Date", "Hour", "Count"]

        mean = hourly["Count"].mean()
        std = hourly["Count"].std()
        if std == 0:
            hourly["z_score"] = 0.0
        else:
            hourly["z_score"] = ((hourly["Count"] - mean) / std).round(2)

        anomalies = hourly[hourly["z_score"].abs() > self.z_threshold].copy()
        anomalies["direction"] = np.where(anomalies["z_score"] > 0, "SPIKE", "DROP")
        return anomalies.sort_values("z_score", ascending=False)

    def detect_user_anomalies(self) -> pd.DataFrame:
        """
        Find users with unusually high daily event counts.

        Flags users whose daily usage is more than `z_threshold` standard
        deviations above the mean daily usage across all users.
        """
        daily_user = (
            self.df.groupby(["Date", "PersonnelNr", "LastName", "FirstName"])
            .size()
            .reset_index(name="DailyCount")
        )

        mean = daily_user["DailyCount"].mean()
        std = daily_user["DailyCount"].std()
        if std == 0:
            return pd.DataFrame()

        daily_user["z_score"] = ((daily_user["DailyCount"] - mean) / std).round(2)
        anomalies = daily_user[daily_user["z_score"] > self.z_threshold].copy()
        return anomalies.sort_values("z_score", ascending=False)

    def detect_off_hours_access(
        self, start_hour: int = 7, end_hour: int = 20, exclude_weekends: bool = True
    ) -> pd.DataFrame:
        """
        Find access events outside normal business hours.

        Args:
            start_hour: Business hours start (default: 07:00).
            end_hour: Business hours end (default: 20:00).
            exclude_weekends: If True, all weekend events are flagged.
        """
        mask = (self.df["Hour"] < start_hour) | (self.df["Hour"] >= end_hour)

        if exclude_weekends:
            weekend = self.df["DayOfWeek"].isin(["Saturday", "Sunday"])
            mask = mask | weekend

        off_hours = self.df[mask].copy()
        off_hours["Reason"] = "Off-hours access"
        off_hours.loc[
            off_hours["DayOfWeek"].isin(["Saturday", "Sunday"]), "Reason"
        ] = "Weekend access"

        return off_hours[
            ["EventTime", "PersonnelNr", "LastName", "FirstName",
             "AccessPointName", "Granted", "Reason"]
        ].sort_values("EventTime", ascending=False)
