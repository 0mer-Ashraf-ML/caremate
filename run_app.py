# # run_app.py
# #!/usr/bin/env python3
# """
# Main application runner for CareMate Phase 1
# """

# import sys
# import os
# import subprocess
# import threading
# import time
# from pathlib import Path

# def setup_environment():
#     """Setup the application environment"""
#     print("🔧 Setting up CareMate environment...")
    
#     # Create necessary directories
#     dirs_to_create = [
#         "./data",
#         "./output/generated", 
#         "./output/temp",
#         "./templates/forms",
#         "./templates/layouts"
#     ]
    
#     for dir_path in dirs_to_create:
#         Path(dir_path).mkdir(parents=True, exist_ok=True)
#         print(f"✅ Created directory: {dir_path}")
    
#     # Setup database
#     print("🗄️ Initializing database...")
#     try:
#         from scripts.setup_ndis_db import create_database
#         create_database()
#     except ImportError:
#         print("⚠️ Running database setup script...")
#         subprocess.run([sys.executable, "scripts/setup_db.py"], check=True)
    
#     # Create template files
#     print("📄 Creating template files...")
#     try:
#         from scripts.populate_templates import create_template_files, create_layout_files
#         create_template_files()
#         create_layout_files()
#     except ImportError:
#         print("⚠️ Running template population script...")
#         subprocess.run([sys.executable, "scripts/populate_templates.py"], check=True)
    
#     print("✅ Environment setup complete!")

# def check_dependencies():
#     """Check if all required dependencies are installed"""
#     print("📦 Checking dependencies...")
    
#     required_packages = [
#         "streamlit", "fastapi", "uvicorn", "sqlite3", 
#         "pydantic", "jinja2", "reportlab", "python-docx"
#     ]
    
#     missing_packages = []
    
#     for package in required_packages:
#         try:
#             if package == "sqlite3":
#                 import sqlite3
#             else:
#                 __import__(package)
#             print(f"✅ {package}")
#         except ImportError:
#             missing_packages.append(package)
#             print(f"❌ {package}")
    
#     if missing_packages:
#         print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
#         print("Please run: pip install -r requirements.txt")
#         return False
    
#     print("✅ All dependencies satisfied!")
#     return True

# def run_backend():
#     """Run the FastAPI backend"""
#     print("🚀 Starting backend server...")
#     try:
#         import uvicorn
#         from backend.main import app
#         uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
#     except Exception as e:
#         print(f"❌ Backend failed to start: {e}")

# def run_frontend():
#     """Run the Streamlit frontend"""
#     print("🚀 Starting frontend application...")
#     try:
#         # Give backend time to start
#         time.sleep(2)
#         subprocess.run([
#             sys.executable, "-m", "streamlit", "run", "app.py",
#             "--server.port", "8501",
#             "--server.address", "0.0.0.0"
#         ])
#     except Exception as e:
#         print(f"❌ Frontend failed to start: {e}")

# def main():
#     """Main application runner"""
#     print("🏠 CareMate Phase 1 - AI Form Assistant")
#     print("=" * 50)
    
#     # Check dependencies
#     if not check_dependencies():
#         sys.exit(1)
    
#     # Setup environment
#     setup_environment()
    
#     print("\n🚀 Starting CareMate applications...")
    
#     # For development, we'll just run the Streamlit app
#     # In production, you might want to run both backend and frontend
    
#     choice = input("\nChoose mode:\n1. Frontend only (Streamlit)\n2. Backend + Frontend\n3. Backend only\nEnter choice (1-3): ").strip()
    
#     if choice == "1" or choice == "":
#         print("\n🎯 Starting Streamlit frontend...")
#         subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    
#     elif choice == "2":
#         print("\n🎯 Starting both backend and frontend...")
#         # Start backend in thread
#         backend_thread = threading.Thread(target=run_backend, daemon=True)
#         backend_thread.start()
        
#         # Start frontend in main thread
#         run_frontend()
    
#     elif choice == "3":
#         print("\n🎯 Starting backend only...")
#         run_backend()
    
#     else:
#         print("❌ Invalid choice. Exiting.")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()