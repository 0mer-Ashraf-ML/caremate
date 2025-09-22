# tests/test_ndis_services.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.services.ai_service import NDISAIService
from backend.services.client_service import ClientService
from backend.services.coordinator_service import CoordinatorService

class TestNDISAIService:
    """Test NDIS AI service functionality"""
    
    def setup_method(self):
        self.ai_service = NDISAIService()
    
    @pytest.mark.asyncio
    async def test_document_generation(self):
        """Test NDIS document generation"""
        client_data = {
            "full_name": "John Smith",
            "ndis_number": "123456789",
            "conditions": ["Autism Spectrum Disorder"]
        }
        
        coordinator_data = {
            "coordinator_name": "Jane Doe",
            "provider_name": "Support Services Inc"
        }
        
        result = await self.ai_service.generate_ndis_document(
            template_type="progress_report",
            client_data=client_data,
            coordinator_data=coordinator_data,
            context="Quarterly progress review",
            supporting_docs=[]
        )
        
        assert isinstance(result, str)
        assert "John Smith" in result
        assert "progress" in result.lower()

class TestClientService:
    """Test client service functionality"""
    
    def setup_method(self):
        self.client_service = ClientService()
    
    def test_client_creation(self):
        """Test client folder creation"""
        from backend.models.client import ClientFolderCreate
        
        client_data = ClientFolderCreate(
            coordinator_id=1,
            full_name="Test Client",
            ndis_number="987654321",
            conditions=["Physical Disability"],
            goals_advocacy=True
        )
        
        # Mock the database operations
        with patch.object(self.client_service.db, 'execute_insert') as mock_insert:
            mock_insert.return_value = 1
            
            with patch.object(self.client_service, 'get_client_by_id') as mock_get:
                mock_client = Mock()
                mock_client.full_name = "Test Client"
                mock_get.return_value = mock_client
                
                result = self.client_service.create_client_folder(client_data)
                assert result.full_name == "Test Client"