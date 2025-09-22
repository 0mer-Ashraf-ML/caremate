# backend/services/coordinator_service.py - UPDATED
from typing import Optional
from config.database import DatabaseManager
from backend.models.coordinator import CoordinatorProfile, CoordinatorProfileCreate
from datetime import datetime

class CoordinatorService:
    """Service for coordinator profile management with database integration"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_coordinator_profile(self, profile_data: CoordinatorProfileCreate) -> CoordinatorProfile:
        """Create coordinator profile in database"""
        try:
            # Check if email already exists
            existing = self.get_coordinator_by_email(profile_data.email)
            if existing:
                raise Exception(f"Coordinator with email {profile_data.email} already exists")
            
            # Insert into database
            query = """
                INSERT INTO coordinator_profiles 
                (provider_name, coordinator_name, email, phone, profile_complete, credits_balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            coordinator_id = self.db.execute_insert(query, (
                profile_data.provider_name,
                profile_data.coordinator_name,
                profile_data.email,
                profile_data.phone,
                True,  # profile_complete
                100    # default credits
            ))
            
            # Return the created profile
            return self.get_coordinator_by_id(coordinator_id)
            
        except Exception as e:
            raise Exception(f"Failed to create coordinator profile: {str(e)}")
    
    def get_coordinator_by_id(self, coordinator_id: int) -> Optional[CoordinatorProfile]:
        """Get coordinator by ID from database"""
        try:
            query = "SELECT * FROM coordinator_profiles WHERE id = ?"
            result = self.db.execute_query(query, (coordinator_id,))
            
            if not result:
                return None
            
            row = dict(result[0])
            
            # Convert to CoordinatorProfile model
            return CoordinatorProfile(
                id=row['id'],
                provider_name=row['provider_name'],
                coordinator_name=row['coordinator_name'],
                email=row['email'],
                phone=row['phone'],
                profile_complete=bool(row['profile_complete']),
                credits_balance=row['credits_balance'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
        except Exception as e:
            print(f"Error getting coordinator by ID: {e}")
            return None
    
    def get_coordinator_by_email(self, email: str) -> Optional[CoordinatorProfile]:
        """Get coordinator by email from database"""
        try:
            query = "SELECT * FROM coordinator_profiles WHERE email = ?"
            result = self.db.execute_query(query, (email,))
            
            if not result:
                return None
            
            row = dict(result[0])
            
            return CoordinatorProfile(
                id=row['id'],
                provider_name=row['provider_name'],
                coordinator_name=row['coordinator_name'],
                email=row['email'],
                phone=row['phone'],
                profile_complete=bool(row['profile_complete']),
                credits_balance=row['credits_balance'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
        except Exception as e:
            print(f"Error getting coordinator by email: {e}")
            return None
    
    def update_credits(self, coordinator_id: int, credit_change: int) -> bool:
        """Update coordinator credits (positive to add, negative to subtract)"""
        try:
            # Get current balance first
            current_balance = self.get_credits_balance(coordinator_id)
            new_balance = current_balance + credit_change
            
            # Prevent negative balance
            if new_balance < 0:
                raise Exception("Insufficient credits")
            
            query = """
                UPDATE coordinator_profiles 
                SET credits_balance = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.db.execute_query(query, (new_balance, coordinator_id))
            return True
            
        except Exception as e:
            print(f"Error updating credits: {e}")
            return False
    
    def get_credits_balance(self, coordinator_id: int) -> int:
        """Get current credits balance from database"""
        try:
            query = "SELECT credits_balance FROM coordinator_profiles WHERE id = ?"
            result = self.db.execute_query(query, (coordinator_id,))
            
            if result:
                return result[0]['credits_balance']
            return 0
            
        except Exception as e:
            print(f"Error getting credits balance: {e}")
            return 0