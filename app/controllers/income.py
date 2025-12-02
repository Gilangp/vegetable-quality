from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.income import Income
from app.models.family import Family
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse, IncomeMonthlySummary
from fastapi import HTTPException


class IncomeController:
    
    @staticmethod
    def list_incomes(db: Session, family_id: int = None, category: str = None, 
                     start_date: datetime = None, end_date: datetime = None, skip: int = 0, limit: int = 100):
        """List all incomes with optional filtering"""
        query = db.query(Income)
        
        if family_id:
            query = query.filter(Income.family_id == family_id)
        
        if category:
            query = query.filter(Income.category == category)
        
        if start_date:
            query = query.filter(Income.date >= start_date)
        
        if end_date:
            query = query.filter(Income.date <= end_date)
        
        return query.order_by(Income.date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_income(db: Session, income_id: int):
        """Get single income by ID"""
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        return income
    
    @staticmethod
    def create_income(db: Session, income_data: IncomeCreate, user_id: int = None):
        """Create new income"""
        # Validate family exists
        family = db.query(Family).filter(Family.id == income_data.family_id).first()
        if not family:
            raise HTTPException(status_code=404, detail="Family not found")
        
        # Create income record
        db_income = Income(
            family_id=income_data.family_id,
            amount=income_data.amount,
            category=income_data.category,
            source=income_data.source,
            date=income_data.date,
            notes=income_data.notes,
            created_by=user_id
        )
        
        db.add(db_income)
        db.commit()
        db.refresh(db_income)
        return db_income
    
    @staticmethod
    def update_income(db: Session, income_id: int, income_data: IncomeUpdate):
        """Update income"""
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        
        # Update only provided fields
        if income_data.amount is not None:
            income.amount = income_data.amount
        
        if income_data.category is not None:
            income.category = income_data.category
        
        if income_data.source is not None:
            income.source = income_data.source
        
        if income_data.date is not None:
            income.date = income_data.date
        
        if income_data.notes is not None:
            income.notes = income_data.notes
        
        db.commit()
        db.refresh(income)
        return income
    
    @staticmethod
    def delete_income(db: Session, income_id: int):
        """Delete income"""
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        
        db.delete(income)
        db.commit()
        return {"message": "Income deleted successfully"}
    
    @staticmethod
    def get_monthly_summary(db: Session, family_id: int = None, year: int = None, month: int = None):
        """Get monthly income summary"""
        query = db.query(Income)
        
        if family_id:
            query = query.filter(Income.family_id == family_id)
        
        if year and month:
            # Filter by specific year and month
            query = query.filter(
                func.year(Income.date) == year,
                func.month(Income.date) == month
            )
        else:
            # Default to current month
            today = datetime.now()
            year = today.year
            month = today.month
            query = query.filter(
                func.year(Income.date) == year,
                func.month(Income.date) == month
            )
        
        incomes = query.all()
        
        if not incomes:
            return IncomeMonthlySummary(
                year=year,
                month=month,
                total_income=Decimal(0),
                transaction_count=0,
                by_category={}
            )
        
        # Calculate totals
        total_income = sum(Decimal(str(inc.amount)) for inc in incomes)
        
        # Calculate by category
        by_category = {}
        for income in incomes:
            if income.category not in by_category:
                by_category[income.category] = 0
            by_category[income.category] += float(income.amount)
        
        return IncomeMonthlySummary(
            year=year,
            month=month,
            total_income=total_income,
            transaction_count=len(incomes),
            by_category=by_category
        )
