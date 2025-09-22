import json
from typing import Dict, Any, List, Optional
from config.database import DatabaseManager
from backend.models.client import ClientFolder, ClientFolderCreate, ClientDocument
from backend.services.extraction_service import ExtractionService   # ✅ NEW
from datetime import datetime


class ClientService:
    """Service for managing client folders and documents"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.extractor = ExtractionService()   # ✅ init Gemini extractor
    
    def create_client_folder(self, client_data: ClientFolderCreate) -> ClientFolder:
        """Create new client folder"""
        try:
            conditions_json = json.dumps(client_data.conditions or [])
            
            query = """
                INSERT INTO client_folders 
                (coordinator_id, full_name, ndis_number, plan_start_date, plan_end_date,
                 email, phone, conditions, coordinator_notes, goals_advocacy, goals_support,
                 goals_capacity_building, goals_funding_increase, goals_other)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            client_id = self.db.execute_insert(query, (
                client_data.coordinator_id,
                client_data.full_name,
                client_data.ndis_number,
                client_data.plan_start_date,
                client_data.plan_end_date,
                client_data.email,
                client_data.phone,
                conditions_json,
                client_data.coordinator_notes,
                client_data.goals_advocacy,
                client_data.goals_support,
                client_data.goals_capacity_building,
                client_data.goals_funding_increase,
                client_data.goals_other
            ))
            
            return self.get_client_by_id(client_id)
            
        except Exception as e:
            raise Exception(f"Failed to create client folder: {str(e)}")
        
    def update_client_folder(self, client_data: ClientFolder) -> None:
        """Update existing client folder"""
        query = """
            UPDATE client_folders
            SET full_name=?, ndis_number=?, plan_start_date=?, plan_end_date=?,
                email=?, phone=?, conditions=?, coordinator_notes=?,
                goals_advocacy=?, goals_support=?, goals_capacity_building=?,
                goals_funding_increase=?, goals_other=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        self.db.execute_query(query, (
            client_data.full_name,
            client_data.ndis_number,
            client_data.plan_start_date,
            client_data.plan_end_date,
            client_data.email,
            client_data.phone,
            json.dumps(client_data.conditions or []),
            client_data.coordinator_notes,
            client_data.goals_advocacy,
            client_data.goals_support,
            client_data.goals_capacity_building,
            client_data.goals_funding_increase,
            client_data.goals_other,
            client_data.id
        ))

    def get_client_by_id(self, client_id: int) -> Optional[ClientFolder]:
        """Get client folder by ID"""
        query = "SELECT * FROM client_folders WHERE id = ?"
        result = self.db.execute_query(query, (client_id,))
        
        if result:
            client_dict = dict(result[0])
            # Parse conditions JSON
            if client_dict['conditions']:
                try:
                    client_dict['conditions'] = json.loads(client_dict['conditions'])
                except:
                    client_dict['conditions'] = []
            
            return ClientFolder(**client_dict)
        return None
    
    def get_coordinator_clients(self, coordinator_id: int) -> List[ClientFolder]:
        """Get all clients for a coordinator"""
        query = "SELECT * FROM client_folders WHERE coordinator_id = ? ORDER BY full_name"
        results = self.db.execute_query(query, (coordinator_id,))
        
        clients = []
        for row in results:
            client_dict = dict(row)
            if client_dict['conditions']:
                try:
                    client_dict['conditions'] = json.loads(client_dict['conditions'])
                except:
                    client_dict['conditions'] = []
            clients.append(ClientFolder(**client_dict))
        
        return clients
    
    def add_client_document(
        self, client_id: int, document_name: str, 
        document_type: str, file_path: str, content: str = ""
    ) -> int:
        """Add document to client folder + run AI extraction"""
        try:
            # ✅ Extract structured JSON with Gemini
            extracted_json = self.extractor.extract_json_from_file(file_path)

            query = """
                INSERT INTO client_documents 
                (client_id, document_name, document_type, file_path, extracted_content)
                VALUES (?, ?, ?, ?, ?)
            """
            
            return self.db.execute_insert(query, (
                client_id,
                document_name,
                document_type,
                file_path,
                json.dumps(extracted_json, ensure_ascii=False)  # store structured JSON
            ))
        
        except Exception as e:
            raise Exception(f"Failed to add client document: {str(e)}")
    
    def get_client_documents(self, client_id: int) -> List[ClientDocument]:
        """Get all documents for a client"""
        query = "SELECT * FROM client_documents WHERE client_id = ? ORDER BY uploaded_at DESC"
        results = self.db.execute_query(query, (client_id,))
        
        return [ClientDocument(**dict(row)) for row in results]
    
def process_and_store_extracted_data(self, client_id: int, template_type: str, file_path: str) -> int:
        """
        Process uploaded document with Gemini → extract structured JSON →
        save into client_extracted_data table.
        """
        try:
            # 1️⃣ Extract JSON from Gemini model
            extracted_json = self.extractor.extract(file_path, template_type)

            # 2️⃣ Save JSON into DB
            query = """
                INSERT INTO client_extracted_data (client_id, template_type, extracted_json, created_at)
                VALUES (?, ?, ?, ?)
            """
            doc_id = self.db.execute_insert(query, (
                client_id,
                template_type,
                json.dumps(extracted_json),
                datetime.now().isoformat()
            ))
            return doc_id
        except Exception as e:
            raise Exception(f"Failed to process and store extracted data: {e}")

