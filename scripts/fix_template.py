# ========================================
# ADDITIONAL HELPER SCRIPT
# ========================================

# scripts/fix_templates.py
#!/usr/bin/env python3
"""Script to fix template population issues"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.setup_ndis_db import fix_template_population, verify_database_data

def main():
    """Fix template population"""
    print("🔧 Fixing template population...")
    
    success = fix_template_population()
    
    if success:
        print("✅ Templates fixed!")
        verify_database_data()
    else:
        print("❌ Failed to fix templates")

if __name__ == "__main__":
    main()