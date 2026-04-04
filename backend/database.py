"""
Database - PostgreSQL connection and schema management
"""

import os
from typing import Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class Database:
    """
    PostgreSQL database manager with connection pooling.
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize database connection pool.
        
        Args:
            connection_string: PostgreSQL connection string
        """
        # Use DATABASE_URL env var for Docker, fallback to localhost for local dev
        self.connection_string = connection_string or os.environ.get(
            'DATABASE_URL', 
            'postgresql://localhost:5432/llmtrader'
        )
        
        # Create connection pool (min 1, max 10 connections)
        self.pool = SimpleConnectionPool(1, 10, self.connection_string)
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Get a cursor from a pooled connection.
        
        Args:
            dict_cursor: Return rows as dictionaries (default: True)
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def create_tables(self):
        """Create all database tables if they don't exist"""
        with self.get_cursor(dict_cursor=False) as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Schwab credentials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schwab_credentials (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    app_key TEXT NOT NULL,
                    app_secret_encrypted TEXT NOT NULL,
                    callback_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Schwab tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schwab_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    token_type VARCHAR(50) DEFAULT 'Bearer',
                    expires_at TIMESTAMP NOT NULL,
                    scope TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # AI API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_api_keys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    service_name VARCHAR(50) NOT NULL,
                    api_key TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, service_name)
                )
            """)
            
            # Managed positions table (for LLM position monitoring)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS managed_positions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    position_id VARCHAR(255) UNIQUE NOT NULL,
                    symbol VARCHAR(50) NOT NULL,
                    position_type VARCHAR(50) NOT NULL,
                    quantity DECIMAL NOT NULL,
                    entry_price DECIMAL NOT NULL,
                    current_price DECIMAL NOT NULL,
                    trade_thesis TEXT NOT NULL,
                    triggers JSONB NOT NULL,
                    option_details JSONB,
                    status VARCHAR(50) DEFAULT 'ACTIVE',
                    registered_at TIMESTAMP DEFAULT NOW(),
                    last_review TIMESTAMP,
                    review_count INTEGER DEFAULT 0,
                    exit_price DECIMAL,
                    exit_reason TEXT,
                    closed_at TIMESTAMP
                )
            """)
            
            # Investment profiles table (KYC / Investment Policy Statement)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    raw_answers JSONB NOT NULL,
                    ai_summary TEXT,
                    summary_model VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Conversation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    conversation_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    model VARCHAR(50),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_schwab_credentials_user_id ON schwab_credentials(user_id);
                CREATE INDEX IF NOT EXISTS idx_schwab_tokens_user_id ON schwab_tokens(user_id);
                CREATE INDEX IF NOT EXISTS idx_ai_api_keys_user_id ON ai_api_keys(user_id);
                CREATE INDEX IF NOT EXISTS idx_managed_positions_user_id ON managed_positions(user_id);
                CREATE INDEX IF NOT EXISTS idx_managed_positions_status ON managed_positions(status);
                CREATE INDEX IF NOT EXISTS idx_conversation_history_user_id ON conversation_history(user_id);
                CREATE INDEX IF NOT EXISTS idx_conversation_history_conversation_id ON conversation_history(conversation_id);
            """)
            
            print("✅ Database tables created successfully")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute("""
                DROP TABLE IF EXISTS conversation_history CASCADE;
                DROP TABLE IF EXISTS managed_positions CASCADE;
                DROP TABLE IF EXISTS ai_api_keys CASCADE;
                DROP TABLE IF EXISTS schwab_tokens CASCADE;
                DROP TABLE IF NOT EXISTS schwab_credentials CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
            """)
            print("⚠️  All tables dropped")
    
    def close(self):
        """Close all connections in the pool"""
        self.pool.closeall()


# Global database instance
db = Database()


if __name__ == "__main__":
    # Create tables when run directly
    db.create_tables()
