"""
Data loader — Extract access events from AEOS SQL Server database.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import pyodbc


def get_connection_string() -> str:
    """Build ODBC connection string from environment variables."""
    driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_NAME", "aeosdb")
    trusted = os.getenv("DB_TRUSTED_CONNECTION", "no").lower() in ("yes", "true", "1")

    if trusted:
        return (
            f"DRIVER={driver};SERVER={server};DATABASE={database};"
            f"Trusted_Connection=yes;TrustServerCertificate=yes;"
        )
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    return (
        f"DRIVER={driver};SERVER={server};DATABASE={database};"
        f"UID={user};PWD={password};TrustServerCertificate=yes;"
    )


EVENTS_QUERY = """
SELECT
    e.EventTime,
    e.EventType,
    e.Granted,
    e.ReaderName,
    p.PersonnelNr,
    p.LastName,
    p.FirstName,
    p.Company,
    ap.Name        AS AccessPointName,
    ap.Id          AS AccessPointId,
    c.BadgeNumber
FROM dbo.Event e WITH (NOLOCK)
LEFT JOIN dbo.Carrier c   WITH (NOLOCK) ON e.CarrierId = c.Id
LEFT JOIN dbo.Person  p   WITH (NOLOCK) ON c.PersonId  = p.Id
LEFT JOIN dbo.AccessPoint ap WITH (NOLOCK) ON e.AccessPointId = ap.Id
WHERE e.EventTime >= ?
  AND e.EventTime <  ?
ORDER BY e.EventTime;
"""


def load_events(days: int = 30) -> pd.DataFrame:
    """
    Load access events from SQL Server into a pandas DataFrame.

    Args:
        days: Number of past days to retrieve.

    Returns:
        DataFrame with columns: EventTime, EventType, Granted, ReaderName,
        PersonnelNr, LastName, FirstName, Company, AccessPointName, etc.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    conn = pyodbc.connect(get_connection_string(), timeout=30)
    try:
        df = pd.read_sql(EVENTS_QUERY, conn, params=[start, end])
    finally:
        conn.close()

    if "EventTime" in df.columns:
        df["EventTime"] = pd.to_datetime(df["EventTime"])
        df["Hour"] = df["EventTime"].dt.hour
        df["DayOfWeek"] = df["EventTime"].dt.day_name()
        df["Date"] = df["EventTime"].dt.date

    return df
