"""
Data Models for Healthcare System

Defines the data structures for patients, lab results, medications, and appointments.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class Gender(str, Enum):
    """Patient gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class LabStatus(str, Enum):
    """Lab result status enumeration."""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    PENDING = "pending"


@dataclass
class Patient:
    """Patient data model."""
    
    patient_id: str
    name: str
    age: int
    gender: Gender
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    emergency_contact: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default values and timestamps."""
        if self.medical_history is None:
            self.medical_history = []
        if self.allergies is None:
            self.allergies = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for MongoDB storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the patient
        """
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """
        Create Patient instance from dictionary.
        
        Args:
            data: Dictionary containing patient data
            
        Returns:
            Patient: Patient instance
        """
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class LabResult:
    """Laboratory test result data model."""
    
    result_id: str
    patient_id: str
    test_name: str
    value: float
    unit: str
    status: LabStatus
    reference_range: Optional[str] = None
    test_date: Optional[datetime] = None
    ordered_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default values and timestamps."""
        if self.test_date is None:
            self.test_date = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for MongoDB storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the lab result
        """
        data = asdict(self)
        data['test_date'] = self.test_date.isoformat() if self.test_date else None
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LabResult':
        """
        Create LabResult instance from dictionary.
        
        Args:
            data: Dictionary containing lab result data
            
        Returns:
            LabResult: LabResult instance
        """
        if 'test_date' in data and data['test_date']:
            data['test_date'] = datetime.fromisoformat(data['test_date'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class Medication:
    """Medication data model."""
    
    medication_id: str
    patient_id: str
    name: str
    dosage: str
    frequency: str
    route: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prescribed_by: Optional[str] = None
    instructions: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default values and timestamps."""
        if self.start_date is None:
            self.start_date = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for MongoDB storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the medication
        """
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat() if self.start_date else None
        data['end_date'] = self.end_date.isoformat() if self.end_date else None
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Medication':
        """
        Create Medication instance from dictionary.
        
        Args:
            data: Dictionary containing medication data
            
        Returns:
            Medication: Medication instance
        """
        if 'start_date' in data and data['start_date']:
            data['start_date'] = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data and data['end_date']:
            data['end_date'] = datetime.fromisoformat(data['end_date'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class Appointment:
    """Appointment data model."""
    
    appointment_id: str
    patient_id: str
    doctor_id: str
    appointment_date: datetime
    duration_minutes: int = 30
    appointment_type: str = "consultation"
    status: str = "scheduled"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default values and timestamps."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for MongoDB storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the appointment
        """
        data = asdict(self)
        data['appointment_date'] = self.appointment_date.isoformat()
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Appointment':
        """
        Create Appointment instance from dictionary.
        
        Args:
            data: Dictionary containing appointment data
            
        Returns:
            Appointment: Appointment instance
        """
        if 'appointment_date' in data and data['appointment_date']:
            data['appointment_date'] = datetime.fromisoformat(data['appointment_date'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data) 