import pytest
from decimal import Decimal
from datetime import datetime
from pydantic_core import ValidationError
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse


class TestIncomeSchema:
    
    def test_create_income_valid(self):
        """Test valid income creation"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "Main Job",
            "date": datetime.now(),
            "notes": "Monthly salary"
        }
        income = IncomeCreate(**income_data)
        assert income.family_id == 1
        assert income.amount == Decimal("500000")
        assert income.category == "Salary"
        assert income.source == "Main Job"
        assert income.notes == "Monthly salary"
    
    def test_create_income_without_notes(self):
        """Test income creation without optional notes"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "Main Job",
            "date": datetime.now()
        }
        income = IncomeCreate(**income_data)
        assert income.notes is None
    
    def test_create_income_empty_category(self):
        """Test income creation with empty category"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "",
            "source": "Main Job",
            "date": datetime.now()
        }
        with pytest.raises((ValueError, ValidationError)):
            IncomeCreate(**income_data)
    
    def test_create_income_empty_source(self):
        """Test income creation with empty source"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "",
            "date": datetime.now()
        }
        with pytest.raises((ValueError, ValidationError)):
            IncomeCreate(**income_data)
    
    def test_create_income_whitespace_category(self):
        """Test income creation with whitespace category"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "   Salary   ",
            "source": "Main Job",
            "date": datetime.now()
        }
        income = IncomeCreate(**income_data)
        assert income.category == "Salary"
    
    def test_create_income_whitespace_source(self):
        """Test income creation with whitespace source"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "   Main Job   ",
            "date": datetime.now()
        }
        income = IncomeCreate(**income_data)
        assert income.source == "Main Job"
    
    def test_create_income_empty_notes(self):
        """Test income creation with empty notes"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "Main Job",
            "date": datetime.now(),
            "notes": ""
        }
        with pytest.raises((ValueError, ValidationError)):
            IncomeCreate(**income_data)
    
    def test_create_income_whitespace_notes(self):
        """Test income creation with whitespace notes"""
        income_data = {
            "family_id": 1,
            "amount": Decimal("500000"),
            "category": "Salary",
            "source": "Main Job",
            "date": datetime.now(),
            "notes": "   Monthly salary   "
        }
        income = IncomeCreate(**income_data)
        assert income.notes == "Monthly salary"
    
    def test_update_income_partial(self):
        """Test partial income update"""
        update_data = {
            "amount": Decimal("600000"),
            "category": "Bonus"
        }
        income_update = IncomeUpdate(**update_data)
        assert income_update.amount == Decimal("600000")
        assert income_update.category == "Bonus"
        assert income_update.source is None
        assert income_update.date is None
    
    def test_update_income_empty_category(self):
        """Test update with empty category"""
        update_data = {
            "category": ""
        }
        with pytest.raises((ValueError, ValidationError)):
            IncomeUpdate(**update_data)
