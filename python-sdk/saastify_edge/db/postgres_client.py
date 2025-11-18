"""
PostgreSQL Database Client

Provides async database operations using asyncpg with support for:
- Cloud SQL Proxy connections (local development)
- Direct Cloud SQL connections (production)
- Local PostgreSQL connections
"""

import asyncpg
from typing import Dict, List, Any, Optional
import logging
from contextlib import asynccontextmanager

from .config import DatabaseConfig, get_db_config

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """Async PostgreSQL client using asyncpg."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize PostgreSQL client.
        
        Args:
            config: Database configuration (uses environment if not provided)
        """
        self.config = config or get_db_config()
        self.pool: Optional[asyncpg.Pool] = None
        
    async def connect(self) -> None:
        """Establish connection pool."""
        if self.pool:
            logger.warning("Connection pool already exists")
            return
        
        try:
            logger.info(f"Connecting to database in {self.config.mode.value} mode")
            
            dsn = self.config.get_asyncpg_dsn()
            
            self.pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=1,
                max_size=self.config.pool_size,
                timeout=self.config.pool_timeout,
                command_timeout=60,
            )
            
            logger.info("Database connection pool created successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """
        Acquire a connection from the pool.
        
        Usage:
            async with client.acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM table")
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def insert(self, table: str, record: Dict[str, Any]) -> str:
        """
        Insert a record into a table.
        
        Args:
            table: Table name
            record: Record data as dictionary
            
        Returns:
            Primary key value (assumes first column is PK)
        """
        columns = list(record.keys())
        values = [record[col] for col in columns]
        placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
        
        query = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES ({placeholders})
            RETURNING *
        """
        
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            # Return first column value (typically the ID)
            return str(row[0]) if row else None
    
    async def insert_batch(self, table: str, records: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple records in a batch.
        
        Args:
            table: Table name
            records: List of records
            
        Returns:
            List of primary key values
        """
        if not records:
            return []
        
        columns = list(records[0].keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
        
        query = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES ({placeholders})
            RETURNING *
        """
        
        ids = []
        async with self.acquire() as conn:
            async with conn.transaction():
                for record in records:
                    values = [record[col] for col in columns]
                    row = await conn.fetchrow(query, *values)
                    ids.append(str(row[0]) if row else None)
        
        return ids
    
    async def update(self, table: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """
        Update records matching filters.
        
        Args:
            table: Table name
            filters: Filter conditions (WHERE clause)
            updates: Fields to update
            
        Returns:
            True if any rows were updated
        """
        set_clauses = []
        where_clauses = []
        values = []
        param_idx = 1
        
        # Build SET clause
        for col, val in updates.items():
            set_clauses.append(f"{col} = ${param_idx}")
            values.append(val)
            param_idx += 1
        
        # Build WHERE clause
        for col, val in filters.items():
            where_clauses.append(f"{col} = ${param_idx}")
            values.append(val)
            param_idx += 1
        
        query = f"""
            UPDATE {table}
            SET {", ".join(set_clauses)}
            WHERE {" AND ".join(where_clauses)}
        """
        
        async with self.acquire() as conn:
            result = await conn.execute(query, *values)
            # Result is like "UPDATE 1"
            return "UPDATE" in result and result.split()[1] != "0"
    
    async def query(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query records from a table.
        
        Args:
            table: Table name
            filters: Optional filter conditions
            
        Returns:
            List of records as dictionaries
        """
        where_clauses = []
        values = []
        param_idx = 1
        
        if filters:
            for col, val in filters.items():
                where_clauses.append(f"{col} = ${param_idx}")
                values.append(val)
                param_idx += 1
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"SELECT * FROM {table} {where_sql}"
        
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *values)
            return [dict(row) for row in rows]
    
    async def get_by_id(self, table: str, record_id: str, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """
        Get a record by ID.
        
        Args:
            table: Table name
            record_id: Record identifier
            id_column: Name of the ID column
            
        Returns:
            Record as dictionary or None
        """
        query = f"SELECT * FROM {table} WHERE {id_column} = $1"
        
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, record_id)
            return dict(row) if row else None
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """
        Delete records matching filters.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            True if any rows were deleted
        """
        where_clauses = []
        values = []
        param_idx = 1
        
        for col, val in filters.items():
            where_clauses.append(f"{col} = ${param_idx}")
            values.append(val)
            param_idx += 1
        
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        
        async with self.acquire() as conn:
            result = await conn.execute(query, *values)
            return "DELETE" in result and result.split()[1] != "0"
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Query result status
        """
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Row as dictionary or None
        """
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Fetch all matching rows.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if database is accessible
        """
        try:
            async with self.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


async def create_db_client(config: Optional[DatabaseConfig] = None) -> PostgreSQLClient:
    """
    Create and connect a PostgreSQL client.
    
    Args:
        config: Optional database configuration
        
    Returns:
        Connected PostgreSQLClient instance
    """
    client = PostgreSQLClient(config)
    await client.connect()
    return client


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_connection():
        """Test database connection."""
        print("Testing database connection...")
        print("=" * 60)
        
        # Load config from environment
        config = get_db_config()
        print(f"Mode: {config.mode.value}")
        print(f"Database: {config.database}")
        
        client = PostgreSQLClient(config)
        
        try:
            await client.connect()
            print("✅ Connection established")
            
            # Health check
            healthy = await client.health_check()
            print(f"✅ Health check: {'PASS' if healthy else 'FAIL'}")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
        finally:
            await client.disconnect()
            print("Connection closed")
    
    asyncio.run(test_connection())
