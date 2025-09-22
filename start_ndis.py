# start_ndis.py
#!/usr/bin/env python3
"""
NDIS Support Coordinator App Startup Script
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_ndis_environment():
    """Setup the NDIS application environment"""
    print("🏥 Setting up NDIS Support Coordinator environment...")
    
    # Create directories
    dirs = [
        "./data",
        "./uploads/client_documents",
        "./output/generated", 
        "./output/temp",
        "./templates/ndis_reports",
        "./logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    # Initialize database
    print("🗄️ Setting up NDIS database...")
    from scripts.setup_ndis_db import create_ndis_database
    create_ndis_database()
    
    # Create template files
    print("📄 Creating NDIS templates...")
    create_ndis_templates()
    
    print("✅ NDIS environment ready!")

def create_ndis_templates():
    """Create NDIS template files"""
    template_dir = Path("./templates/ndis_reports")
    
    templates = {
        "change_of_circumstance.md": """# Change of Circumstance Report

**Report Date:** {{ current_date or "Today" }}

## Participant Information
**Full Name:** {{ participant_name }}
**NDIS Number:** {{ ndis_number }}
**Plan Period:** {{ plan_start_date }} to {{ plan_end_date }}

## Support Coordinator Information  
**Coordinator:** {{ coordinator_name }}
**Provider:** {{ provider_name }}
**Email:** {{ coordinator_email }}

## Reason for Change of Circumstance
{{ context_description }}

## Impact Assessment
{{ impact_analysis or "Assessment of how changes affect current supports and funding." }}

## Current Conditions
{{ conditions_list }}

## Goals Status
{% if goals_advocacy %}• Advocacy support: Active{% endif %}
{% if goals_support %}• Direct support: Active{% endif %}  
{% if goals_capacity_building %}• Capacity building: Active{% endif %}
{% if goals_funding_increase %}• Funding review: Required{% endif %}

## Recommendations
• Plan review recommended due to changed circumstances
• Assessment of modified support needs required
• Consider additional funding allocation if justified

## Supporting Documentation
Supporting evidence has been reviewed and attached.

---
**Coordinator:** {{ coordinator_name }}
**Date:** {{ current_date or "Today" }}
""",

        "progress_report.md": """# Progress Report

**Reporting Period:** {{ reporting_period or "Current Period" }}

## Participant Information
**Name:** {{ participant_name }}
**NDIS Number:** {{ ndis_number }}
**Plan Period:** {{ plan_start_date }} to {{ plan_end_date }}

## Support Coordination Summary
{{ context_description }}

## Progress Towards Outcomes

### Independence and Community Participation
{{ independence_progress or "Progress being monitored through regular contact and service provider feedback." }}

### Health and Wellbeing
{{ health_progress or "Participant's health and wellbeing status monitored through service delivery." }}

## Service Utilization
Current services are being delivered as planned with regular monitoring of effectiveness.

## Achievements This Period
{{ achievements or "Achievements documented through service provider reports and participant feedback." }}

## Challenges and Barriers
{{ challenges or "Any barriers to plan implementation are addressed through ongoing coordination." }}

## Recommendations for Next Period
{{ recommendations or "Continue current support arrangements with regular review." }}

---
**Coordinator:** {{ coordinator_name }}
**Provider:** {{ provider_name }}
**Date:** {{ current_date or "Today" }}
"""
    }
    
    for filename, content in templates.items():
        file_path = template_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Created: {filename}")

def main():
    """Main startup function"""
    print("🏥 NDIS Support Coordinator Document Generator")
    print("=" * 50)
    
    # Setup environment
    setup_ndis_environment()
    
    print("\n🚀 Starting application...")
    
    # Run Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()