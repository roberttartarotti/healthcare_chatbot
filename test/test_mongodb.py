"""
Test MongoDB Client

Tests for MongoDB client and data models.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import pytest
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib_mongodb'))

from mongodb.client import MongoDBClient
from mongodb.models import Patient, Gender, LabResult, LabStatus, Appointment, Medication
from mongodb.exceptions import ConnectionError, MongoDBError


class TestMongoDBClient:
    """Test MongoDB client functionality."""
    
    def test_client_initialization(self):
        """Test MongoDB client initialization."""
        client = MongoDBClient()
        assert client.client is None
        assert client.database is None
        assert "mongodb://" in client.connection_string
    
    def test_client_with_custom_connection_string(self):
        """Test MongoDB client with custom connection string."""
        custom_uri = "mongodb://custom:pass@localhost:27017/test"
        client = MongoDBClient(connection_string=custom_uri)
        assert client.connection_string == custom_uri
    
    @patch('mongodb.client.MongoClient')
    def test_connect_success(self, mock_mongo_client):
        """Test successful MongoDB connection."""
        mock_client = Mock()
        mock_client.admin.command.return_value = {"ok": 1}
        mock_client.get_database.return_value = Mock()
        mock_mongo_client.return_value = mock_client
        
        client = MongoDBClient()
        client.connect()
        
        assert client.client is not None
        assert client.database is not None
        mock_mongo_client.assert_called_once()
    
    @patch('mongodb.client.MongoClient')
    def test_connect_failure(self, mock_mongo_client):
        """Test MongoDB connection failure."""
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        client = MongoDBClient()
        with pytest.raises(ConnectionError):
            client.connect()
    
    def test_disconnect(self):
        """Test MongoDB disconnection."""
        client = MongoDBClient()
        mock_client = Mock()
        client.client = mock_client
        client.database = Mock()
    
        client.disconnect()
    
        assert client.client is None
        assert client.database is None
        mock_client.close.assert_called_once()
    
    def test_get_collection_not_connected(self):
        """Test getting collection when not connected."""
        client = MongoDBClient()
        with pytest.raises(ConnectionError):
            client.get_collection("test")
    
    @patch('mongodb.client.MongoClient')
    def test_insert_one(self, mock_mongo_client):
        """Test inserting a single document."""
        mock_client = Mock()
        mock_client.admin.command.return_value = {"ok": 1}
        mock_database = MagicMock()
        mock_client.get_database.return_value = mock_database
        mock_mongo_client.return_value = mock_client
    
        client = MongoDBClient()
        client.connect()
    
        mock_collection = Mock()
        mock_collection.insert_one.return_value.inserted_id = "test_id"
        mock_database.__getitem__.return_value = mock_collection
        
        result = client.insert_one("test_collection", {"name": "test"})
        
        assert result == "test_id"
        mock_collection.insert_one.assert_called_once_with({"name": "test"})
    
    @patch('mongodb.client.MongoClient')
    def test_find_one(self, mock_mongo_client):
        """Test finding a single document."""
        mock_client = Mock()
        mock_client.admin.command.return_value = {"ok": 1}
        mock_database = MagicMock()
        mock_client.get_database.return_value = mock_database
        mock_mongo_client.return_value = mock_client
    
        client = MongoDBClient()
        client.connect()
    
        mock_collection = Mock()
        mock_collection.find_one.return_value = {"_id": "test_id", "name": "test"}
        mock_database.__getitem__.return_value = mock_collection
        
        result = client.find_one("test_collection", {"name": "test"})
        
        assert result == {"_id": "test_id", "name": "test"}
        mock_collection.find_one.assert_called_once_with({"name": "test"})
    
    @patch('mongodb.client.MongoClient')
    def test_find_many(self, mock_mongo_client):
        """Test finding multiple documents."""
        mock_client = Mock()
        mock_client.admin.command.return_value = {"ok": 1}
        mock_database = MagicMock()
        mock_client.get_database.return_value = mock_database
        mock_mongo_client.return_value = mock_client
    
        client = MongoDBClient()
        client.connect()
    
        mock_collection = Mock()
        mock_collection.find.return_value = [{"_id": "1", "name": "test1"}, {"_id": "2", "name": "test2"}]
        mock_database.__getitem__.return_value = mock_collection
        
        result = client.find_many("test_collection", {"status": "active"})
        
        assert len(result) == 2
        assert result[0]["name"] == "test1"
        assert result[1]["name"] == "test2"
        mock_collection.find.assert_called_once_with({"status": "active"})
    
    def test_context_manager(self):
        """Test MongoDB client as context manager."""
        with patch('mongodb.client.MongoClient') as mock_mongo_client:
            mock_client = Mock()
            mock_client.admin.command.return_value = {"ok": 1}
            mock_client.get_database.return_value = Mock()
            mock_mongo_client.return_value = mock_client
            
            with MongoDBClient() as client:
                assert client.client is not None
                assert client.database is not None
            
            mock_client.close.assert_called_once()


class TestDataModels:
    """Test healthcare data models."""
    
    def test_patient_model(self):
        """Test Patient model creation and serialization."""
        patient = Patient(
            patient_id="P001",
            name="John Doe",
            age=35,
            gender=Gender.MALE,
            email="john@example.com",
            phone="+1234567890",
            medical_history=["diabetes"],
            allergies=["penicillin"]
        )
        
        assert patient.patient_id == "P001"
        assert patient.name == "John Doe"
        assert patient.age == 35
        assert patient.gender == Gender.MALE
        
        patient_dict = patient.to_dict()
        assert patient_dict["patient_id"] == "P001"
        assert patient_dict["name"] == "John Doe"
        assert patient_dict["gender"] == "male"
        
        new_patient = Patient.from_dict(patient_dict)
        assert new_patient.patient_id == patient.patient_id
        assert new_patient.name == patient.name
        assert new_patient.gender == patient.gender
    
    def test_lab_result_model(self):
        """Test LabResult model creation and serialization."""
        lab_result = LabResult(
            result_id="LR001",
            patient_id="P001",
            test_name="glucose",
            value=95.0,
            unit="mg/dL",
            status=LabStatus.NORMAL,
            reference_range="70-100 mg/dL",
            notes="Fasting glucose"
        )
        
        assert lab_result.result_id == "LR001"
        assert lab_result.patient_id == "P001"
        assert lab_result.test_name == "glucose"
        assert lab_result.value == 95.0
        assert lab_result.status == LabStatus.NORMAL
        
        lab_dict = lab_result.to_dict()
        assert lab_dict["result_id"] == "LR001"
        assert lab_dict["test_name"] == "glucose"
        assert lab_dict["status"] == "normal"
        
        new_lab = LabResult.from_dict(lab_dict)
        assert new_lab.result_id == lab_result.result_id
        assert new_lab.test_name == lab_result.test_name
        assert new_lab.status == lab_result.status
    
    def test_appointment_model(self):
        """Test Appointment model creation and serialization."""
        appointment_date = datetime(2025, 7, 25, 14, 0, 0)
        appointment = Appointment(
            appointment_id="APT001",
            patient_id="P001",
            doctor_id="D001",
            appointment_date=appointment_date,
            duration_minutes=30,
            appointment_type="consultation",
            notes="Follow-up visit"
        )
        
        assert appointment.appointment_id == "APT001"
        assert appointment.patient_id == "P001"
        assert appointment.doctor_id == "D001"
        assert appointment.appointment_date == appointment_date
        assert appointment.duration_minutes == 30
        
        apt_dict = appointment.to_dict()
        assert apt_dict["appointment_id"] == "APT001"
        assert apt_dict["appointment_type"] == "consultation"
        
        new_apt = Appointment.from_dict(apt_dict)
        assert new_apt.appointment_id == appointment.appointment_id
        assert new_apt.appointment_type == appointment.appointment_type
    
    def test_medication_model(self):
        """Test Medication model creation and serialization."""
        medication = Medication(
            medication_id="MED001",
            patient_id="P001",
            name="Metformin",
            dosage="500mg",
            frequency="twice daily",
            route="oral",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
            prescribed_by="Dr. Smith",
            instructions="Take with meals",
            is_active=True
        )
        
        assert medication.medication_id == "MED001"
        assert medication.patient_id == "P001"
        assert medication.name == "Metformin"
        assert medication.dosage == "500mg"
        assert medication.frequency == "twice daily"
        assert medication.route == "oral"
        assert medication.is_active is True
        
        med_dict = medication.to_dict()
        assert med_dict["medication_id"] == "MED001"
        assert med_dict["patient_id"] == "P001"
        assert med_dict["name"] == "Metformin"
        assert med_dict["dosage"] == "500mg"
        assert med_dict["frequency"] == "twice daily"
        assert med_dict["route"] == "oral"
        assert med_dict["is_active"] is True
        
        new_med = Medication.from_dict(med_dict)
        assert new_med.medication_id == medication.medication_id
        assert new_med.name == medication.name
        assert new_med.is_active == medication.is_active


class TestEnums:
    """Test enum values."""
    
    def test_gender_enum(self):
        """Test Gender enum values."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.OTHER.value == "other"
    
    def test_lab_status_enum(self):
        """Test LabStatus enum values."""
        assert LabStatus.NORMAL.value == "normal"
        assert LabStatus.ABNORMAL.value == "abnormal"
        assert LabStatus.CRITICAL.value == "critical"
        assert LabStatus.PENDING.value == "pending"


if __name__ == "__main__":
    pytest.main([__file__]) 