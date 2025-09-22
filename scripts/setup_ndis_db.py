# scripts/setup_ndis_db.py
#!/usr/bin/env python3
"""NDIS database setup script with auto template population"""

import sqlite3
import os
from pathlib import Path
from backend.services.template_service import TemplateService

def create_ndis_database():
    """Create SQLite database with NDIS-specific tables"""
    
    # Ensure data directory exists
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "support_coordinator.db"
    print(f"📂 Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("📌 Creating tables...")
        
        # Coordinator profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coordinator_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name VARCHAR(200) NOT NULL,
                coordinator_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                profile_complete BOOLEAN DEFAULT 0,
                credits_balance INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Client folders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coordinator_id INTEGER REFERENCES coordinator_profiles(id),
                full_name VARCHAR(100) NOT NULL,
                ndis_number VARCHAR(20) NOT NULL,
                plan_start_date DATE,
                plan_end_date DATE,
                email VARCHAR(100),
                phone VARCHAR(20),
                conditions TEXT,
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
        
        # Client documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER REFERENCES client_folders(id),
                document_name VARCHAR(255) NOT NULL,
                document_type VARCHAR(50),
                file_path VARCHAR(500),
                extracted_content TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Document templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                template_type VARCHAR(50) NOT NULL,
                template_path VARCHAR(255),
                description TEXT,
                fields_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Generated documents
        cursor.execute("""
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
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Document versions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER REFERENCES generated_documents(id),
                version_number INTEGER,
                content TEXT,
                changes_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Tables created successfully")
        
        # Now ensure templates are in DB
        print("📑 Seeding templates into database...")
        template_service = TemplateService()
        template_service.ensure_templates_in_db()
        print("✅ Templates populated")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def main():
    print("🏥 Setting up NDIS Support Coordinator Database...")
    success = create_ndis_database()
    if success:
        print("🎉 Database setup completed successfully!")
    else:
        print("❌ Database setup failed!")

if __name__ == "__main__":
    main()
