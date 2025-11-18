"""
Database layer for completeness cache and job management
"""

from .completeness_cache import CompletenessWriter, CompletenessReader
from .job_manager import JobStatusUpdater
from .config import DatabaseConfig, ConnectionMode, get_db_config
from .mock_db_client import MockDBClient

# Optional PostgreSQL client (requires asyncpg)
try:
    from .postgres_client import PostgreSQLClient, create_db_client
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    PostgreSQLClient = None
    create_db_client = None

__all__ = [
    "CompletenessWriter",
    "CompletenessReader",
    "JobStatusUpdater",
    "DatabaseConfig",
    "ConnectionMode",
    "get_db_config",
    "PostgreSQLClient",
    "create_db_client",
    "MockDBClient",
]
