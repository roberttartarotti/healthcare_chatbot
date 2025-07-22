# Healthcare MongoDB Library

A Python library for MongoDB operations in healthcare chatbot systems. Provides data models, connection management, and CRUD operations for patient data, lab results, medications, and appointments.

## Features

- 🔗 **Connection Management**: Easy MongoDB connection handling with environment variables
- 📊 **Data Models**: Structured models for healthcare entities (Patient, LabResult, Medication, Appointment)
- 🛡️ **Error Handling**: Custom exceptions for different error scenarios
- 🔧 **Type Safety**: Full type hints and validation
- 📦 **Modern Packaging**: Uses pyproject.toml for modern Python packaging

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd lib_mongodb

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
pip install healthcare-mongodb
```

## Quick Start

### Basic Usage

```python
from healthcare_mongodb import MongoDBClient, Patient, Gender

# Connect to MongoDB
with MongoDBClient() as client:
    # Create a patient
    patient = Patient(
        patient_id="P001",
        name="John Doe",
        age=35,
        gender=Gender.MALE,
        email="john.doe@email.com"
    )
    
    # Insert into database
    patient_id = client.insert_one("patients", patient.to_dict())
    print(f"Patient inserted with ID: {patient_id}")
```

### Environment Variables

Create a `.env` file:

```bash
MONGODB_USER=admin
MONGODB_PASSWORD=your_password
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=healthcare_db
```

## Data Models

### Patient

```python
from healthcare_mongodb import Patient, Gender

patient = Patient(
    patient_id="P001",
    name="Jane Smith",
    age=28,
    gender=Gender.FEMALE,
    medical_history=["asthma"],
    allergies=["penicillin"]
)
```

### LabResult

```python
from healthcare_mongodb import LabResult, LabStatus

lab_result = LabResult(
    result_id="LR001",
    patient_id="P001",
    test_name="Blood Glucose",
    value=95.0,
    unit="mg/dL",
    status=LabStatus.NORMAL,
    reference_range="70-100 mg/dL"
)
```

### Medication

```python
from healthcare_mongodb import Medication

medication = Medication(
    medication_id="M001",
    patient_id="P001",
    name="Metformin",
    dosage="500mg",
    frequency="twice daily",
    route="oral"
)
```

### Appointment

```python
from healthcare_mongodb import Appointment
from datetime import datetime

appointment = Appointment(
    appointment_id="A001",
    patient_id="P001",
    doctor_id="D001",
    appointment_date=datetime(2024, 2, 15, 14, 30),
    appointment_type="consultation"
)
```

## API Reference

### MongoDBClient

#### Connection Management

```python
# Automatic connection with context manager
with MongoDBClient() as client:
    # Your operations here
    pass

# Manual connection
client = MongoDBClient()
client.connect()
# Your operations here
client.disconnect()
```

#### CRUD Operations

```python
# Insert
patient_id = client.insert_one("patients", patient.to_dict())
patient_ids = client.insert_many("patients", [p1.to_dict(), p2.to_dict()])

# Find
patient = client.find_one("patients", {"patient_id": "P001"})
patients = client.find_many("patients", {"age": {"$gte": 30}})

# Update
modified_count = client.update_one("patients", 
    {"patient_id": "P001"}, 
    {"age": 36}
)

# Delete
deleted_count = client.delete_one("patients", {"patient_id": "P001"})
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Building

```bash
# Build package
python -m build

# Install in development mode
pip install -e .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub. 