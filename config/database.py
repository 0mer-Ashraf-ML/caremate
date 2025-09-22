# config/database.py
import sqlite3
from pathlib import Path
from typing import Any, Tuple, List, Optional
from contextlib import contextmanager

class DatabaseManager:
    """SQLite database manager for Support Coordinator app"""

    def __init__(self, db_path: str = "./data/support_coordinator.db"):
        self.db_path = db_path
        self.ensure_db_directory()

    def ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Execute insert query and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute UPDATE or DELETE statements"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount   # number of rows affected

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Return a single row"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchone()

    def fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Return all rows"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()

def init_database():
    """Initialize database with all required tables"""
    db = DatabaseManager()
    
    # Coordinator profiles table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS coordinator_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name VARCHAR(200) NOT NULL,
            coordinator_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            profile_complete BOOLEAN DEFAULT 0,
            credits_balance INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Client folders table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS client_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinator_id INTEGER REFERENCES coordinator_profiles(id),
            full_name VARCHAR(100) NOT NULL,
            ndis_number VARCHAR(20) NOT NULL,
            plan_start_date DATE,
            plan_end_date DATE,
            email VARCHAR(100),
            phone VARCHAR(20),
            conditions TEXT,  -- JSON array
            coordinator_notes TEXT,
            goals_advocacy BOOLEAN DEFAULT 0,
            goals_support BOOLEAN DEFAULT 0,
            goals_capacity_building BOOLEAN DEFAULT 0,
            goals_funding_increase BOOLEAN DEFAULT 0,
            goals_other TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Client documents table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS client_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER REFERENCES client_folders(id),
            document_name VARCHAR(255) NOT NULL,
            document_type VARCHAR(50),  -- 'ot_report', 'ndis_plan', 'other'
            file_path VARCHAR(500),
            extracted_content TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Document templates table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            template_type VARCHAR(50) NOT NULL,  -- 'change_of_circumstance', etc.
            template_path VARCHAR(255),
            description TEXT,
            fields_config TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Generated documents table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS generated_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinator_id INTEGER REFERENCES coordinator_profiles(id),
            client_id INTEGER REFERENCES client_folders(id),
            template_id INTEGER REFERENCES document_templates(id),
            document_name VARCHAR(255),
            content TEXT,
            output_path VARCHAR(500),
            version INTEGER DEFAULT 1,
            credits_used INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'draft',  -- 'draft', 'final'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Document versions table (for edit tracking)
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER REFERENCES generated_documents(id),
            version_number INTEGER,
            content TEXT,
            changes_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)