"""
Data loader — Extract access events from AEOS SQL Server database.

Uses the SQL view `vw_AeosEventLog` which exposes the AEOS internal event
log with columns aligned to the WSDL EventInfo schema:

    Id, EventTypeId, EventTypeName, DateTime, HostName,
    AccesspointId, AccesspointName, EntranceId, EntranceName,
    IdentifierId, Identifier, CarrierId, CarrierFullName

The `Granted` boolean is derived from EventTypeName:
  - "Access granted*"  →  True
  - "Access denied*"   →  False
  - Other events       →  NaN (excluded from grant/deny analysis)
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


# ---------------------------------------------------------------------------
# SQL Query — vw_AeosEventLog (AEOS WSDL EventInfo column naming)
# ---------------------------------------------------------------------------
# This view must be created by the DBA to expose the AEOS internal event
# table with standardized column names matching the SOAP WSDL schema.
#
# See README.md for the CREATE VIEW template.
# ---------------------------------------------------------------------------

EVENTS_QUERY = """
SELECT
    ev.[DateTime],
    ev.EventTypeName,
    ev.AccesspointId,
    ev.AccesspointName,
    ev.EntranceId,
    ev.EntranceName,
    ev.CarrierId,
    ev.CarrierFullName,
    ev.IdentifierId,
    ev.Identifier,
    ev.HostName
FROM dbo.vw_AeosEventLog ev WITH (NOLOCK)
WHERE ev.[DateTime] >= ?
  AND ev.[DateTime] <  ?
ORDER BY ev.[DateTime];
"""


def load_events(days: int = 30) -> pd.DataFrame:
    """
    Load access events from the AEOS SQL Server view into a pandas DataFrame.

    Args:
        days: Number of past days to retrieve.

    Returns:
        DataFrame with AEOS EventInfo columns plus derived fields:
        - Granted (bool): True for "Access granted*", False for "Access denied*"
        - Hour (int): Hour of day (0-23)
        - DayOfWeek (str): Day name
        - Date: Date part of DateTime
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    conn = pyodbc.connect(get_connection_string(), timeout=30)
    try:
        df = pd.read_sql(EVENTS_QUERY, conn, params=[start, end])
    finally:
        conn.close()

    if "DateTime" in df.columns:
        df["DateTime"] = pd.to_datetime(df["DateTime"])
        df["Hour"] = df["DateTime"].dt.hour
        df["DayOfWeek"] = df["DateTime"].dt.day_name()
        df["Date"] = df["DateTime"].dt.date

    # Derive Granted boolean from AEOS EventTypeName
    if "EventTypeName" in df.columns:
        df["Granted"] = df["EventTypeName"].apply(_classify_granted)

    return df


def _classify_granted(event_type_name: str) -> object:
    """
    Classify an AEOS EventTypeName into granted/denied.

    AEOS event types are descriptive strings, not booleans:
      - "Access granted"                     → True
      - "Access granted (first person)"      → True
      - "Access granted with extended unlock" → True
      - "Access denied"                      → False
      - "Access denied: badge not valid"     → False
      - "Access denied: badge blocked"       → False
      - "Access denied: no authorisation"    → False
      - "Access denied: antipassback"        → False
      - "Door forced open"                   → None (alarm, not grant/deny)
      - "Door held open"                     → None
      - "Tailgating"                         → None
    """
    if not isinstance(event_type_name, str):
        return None
    lower = event_type_name.lower().strip()
    if lower.startswith("access granted"):
        return True
    if lower.startswith("access denied"):
        return False
    return None  # Alarm or other event type
