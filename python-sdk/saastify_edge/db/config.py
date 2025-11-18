"""
Database Configuration

Supports:
- Direct connection to GCP Cloud SQL PostgreSQL (production)
- Connection via Cloud SQL Proxy (local development)
- Environment-based configuration
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ConnectionMode(str, Enum):
    """Database connection mode"""
    DIRECT = "direct"  # Direct connection to Cloud SQL
    PROXY = "proxy"    # Via Cloud SQL Proxy
    LOCAL = "local"    # Local PostgreSQL


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    
    # Connection mode
    mode: ConnectionMode = ConnectionMode.PROXY
    
    # Direct connection (production)
    instance_connection_name: Optional[str] = None  # project:region:instance
    database: str = "saastify_edge"
    user: str = "postgres"
    password: Optional[str] = None
    
    # Proxy connection (local development)
    proxy_host: str = "localhost"
    proxy_port: int = 5432
    
    # Local PostgreSQL
    local_host: str = "localhost"
    local_port: int = 5432
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SSL settings
    use_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_root_cert_path: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
        - DB_MODE: Connection mode (direct, proxy, local)
        - DB_INSTANCE: GCP instance connection name (project:region:instance)
        - DB_NAME: Database name
        - DB_USER: Database user
        - DB_PASSWORD: Database password
        - DB_PROXY_HOST: Proxy host (default: localhost)
        - DB_PROXY_PORT: Proxy port (default: 5432)
        - DB_LOCAL_HOST: Local PostgreSQL host
        - DB_LOCAL_PORT: Local PostgreSQL port
        - DB_POOL_SIZE: Connection pool size
        - DB_USE_SSL: Enable SSL (true/false)
        """
        mode_str = os.getenv("DB_MODE", "proxy").lower()
        mode = ConnectionMode(mode_str)
        
        return cls(
            mode=mode,
            instance_connection_name=os.getenv("DB_INSTANCE"),
            database=os.getenv("DB_NAME", "saastify_edge"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            proxy_host=os.getenv("DB_PROXY_HOST", "localhost"),
            proxy_port=int(os.getenv("DB_PROXY_PORT", "5432")),
            local_host=os.getenv("DB_LOCAL_HOST", "localhost"),
            local_port=int(os.getenv("DB_LOCAL_PORT", "5432")),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            use_ssl=os.getenv("DB_USE_SSL", "true").lower() == "true",
            ssl_cert_path=os.getenv("DB_SSL_CERT"),
            ssl_key_path=os.getenv("DB_SSL_KEY"),
            ssl_root_cert_path=os.getenv("DB_SSL_ROOT_CERT"),
        )
    
    def get_connection_string(self) -> str:
        """
        Get SQLAlchemy connection string based on mode.
        
        Returns:
            Database connection URL
        """
        if self.mode == ConnectionMode.DIRECT:
            return self._get_direct_connection_string()
        elif self.mode == ConnectionMode.PROXY:
            return self._get_proxy_connection_string()
        else:  # LOCAL
            return self._get_local_connection_string()
    
    def _get_direct_connection_string(self) -> str:
        """Get connection string for direct Cloud SQL connection."""
        if not self.instance_connection_name:
            raise ValueError("instance_connection_name required for direct mode")
        
        # Format: postgresql+pg8000://user:pass@/dbname?unix_sock=/cloudsql/instance
        # Or use Cloud SQL Python Connector
        return (
            f"postgresql+pg8000://{self.user}:{self.password}@"
            f"/{self.database}?unix_sock=/cloudsql/{self.instance_connection_name}"
        )
    
    def _get_proxy_connection_string(self) -> str:
        """Get connection string for Cloud SQL Proxy connection."""
        password_part = f":{self.password}" if self.password else ""
        return (
            f"postgresql://{self.user}{password_part}@"
            f"{self.proxy_host}:{self.proxy_port}/{self.database}"
        )
    
    def _get_local_connection_string(self) -> str:
        """Get connection string for local PostgreSQL."""
        password_part = f":{self.password}" if self.password else ""
        return (
            f"postgresql://{self.user}{password_part}@"
            f"{self.local_host}:{self.local_port}/{self.database}"
        )
    
    def get_asyncpg_dsn(self) -> str:
        """
        Get asyncpg DSN for async connections.
        
        Returns:
            DSN string for asyncpg
        """
        if self.mode == ConnectionMode.PROXY:
            host = self.proxy_host
            port = self.proxy_port
        elif self.mode == ConnectionMode.LOCAL:
            host = self.local_host
            port = self.local_port
        else:
            # Direct mode with asyncpg requires special handling
            raise NotImplementedError("Direct mode with asyncpg requires Cloud SQL Python Connector")
        
        password_part = f":{self.password}" if self.password else ""
        return f"postgresql://{self.user}{password_part}@{host}:{port}/{self.database}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excludes sensitive data)."""
        return {
            "mode": self.mode.value,
            "database": self.database,
            "user": self.user,
            "proxy_host": self.proxy_host if self.mode == ConnectionMode.PROXY else None,
            "proxy_port": self.proxy_port if self.mode == ConnectionMode.PROXY else None,
            "local_host": self.local_host if self.mode == ConnectionMode.LOCAL else None,
            "local_port": self.local_port if self.mode == ConnectionMode.LOCAL else None,
            "instance": self.instance_connection_name if self.mode == ConnectionMode.DIRECT else None,
            "pool_size": self.pool_size,
            "use_ssl": self.use_ssl,
        }


def get_db_config() -> DatabaseConfig:
    """
    Get database configuration from environment.
    
    Returns:
        DatabaseConfig instance
    """
    return DatabaseConfig.from_env()


# Example usage configurations
EXAMPLE_CONFIGS = {
    "production": """
# Production - Direct Cloud SQL connection
export DB_MODE=direct
export DB_INSTANCE=my-project:us-central1:my-instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-secure-password
export DB_USE_SSL=true
""",
    
    "local_proxy": """
# Local Development - Cloud SQL Proxy
# Start proxy: cloud-sql-proxy my-project:us-central1:my-instance
export DB_MODE=proxy
export DB_PROXY_HOST=localhost
export DB_PROXY_PORT=5432
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
""",
    
    "local_postgres": """
# Local PostgreSQL
export DB_MODE=local
export DB_LOCAL_HOST=localhost
export DB_LOCAL_PORT=5432
export DB_NAME=saastify_edge_dev
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_USE_SSL=false
"""
}


if __name__ == "__main__":
    # Print example configuration
    print("Database Configuration Examples")
    print("=" * 60)
    
    for env_name, config_example in EXAMPLE_CONFIGS.items():
        print(f"\n{env_name.upper()}:")
        print(config_example)
    
    # Show current configuration
    print("\nCurrent Configuration (from environment):")
    print("=" * 60)
    try:
        config = get_db_config()
        print(f"Mode: {config.mode.value}")
        print(f"Database: {config.database}")
        print(f"User: {config.user}")
        
        if config.mode == ConnectionMode.PROXY:
            print(f"Proxy: {config.proxy_host}:{config.proxy_port}")
        elif config.mode == ConnectionMode.LOCAL:
            print(f"Local: {config.local_host}:{config.local_port}")
        elif config.mode == ConnectionMode.DIRECT:
            print(f"Instance: {config.instance_connection_name}")
        
        print(f"\nConnection String (password masked):")
        conn_str = config.get_connection_string()
        # Mask password in output
        if config.password:
            conn_str = conn_str.replace(config.password, "***")
        print(conn_str)
    except Exception as e:
        print(f"Error: {e}")
        print("\nSet environment variables to configure database connection.")
