from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.controllers.income import IncomeController
from app.controllers.dependencies import get_db, get_current_user
from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse,
    IncomeMonthlySummary
)
from app.models.user import User


router = APIRouter(prefix="/incomes", tags=["incomes"])


@router.get("", response_model=List[IncomeResponse])
def list_incomes(
    family_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all incomes with optional filtering
    - Require auth
    
    Query params:
    - family_id: filter by family (optional)
    - category: filter by category (optional)
    - start_date: filter from date (optional)
    - end_date: filter to date (optional)
    - skip: offset (default 0)
    - limit: max results (default 100)
    """
    controller = IncomeController()
    return controller.list_incomes(
        db=db,
        family_id=family_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
def create_income(
    income_data: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new income
    - Require auth
    
    Request body:
    - family_id: Family ID (required)
    - amount: Income amount (required)
    - category: Income category (required, will be trimmed)
    - source: Income source (required, will be trimmed)
    - date: Income date (required)
    - notes: Additional notes (optional, will be trimmed)
    """
    controller = IncomeController()
    return controller.create_income(db=db, income_data=income_data, user_id=current_user.id)


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get income by ID
    - Require auth
    
    Path params:
    - income_id: Income ID (required)
    """
    controller = IncomeController()
    return controller.get_income(db=db, income_id=income_id)


@router.put("/{income_id}", response_model=IncomeResponse)
def update_income(
    income_id: int,
    income_data: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update income
    - Require auth
    
    Path params:
    - income_id: Income ID (required)
    
    Request body:
    - amount: Income amount (optional)
    - category: Income category (optional, will be trimmed)
    - source: Income source (optional, will be trimmed)
    - date: Income date (optional)
    - notes: Additional notes (optional, will be trimmed)
    """
    controller = IncomeController()
    return controller.update_income(db=db, income_id=income_id, income_data=income_data)


@router.delete("/{income_id}")
def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete income
    - Require auth
    
    Path params:
    - income_id: Income ID (required)
    """
    controller = IncomeController()
    return controller.delete_income(db=db, income_id=income_id)


@router.get("/summary/monthly", response_model=IncomeMonthlySummary)
def get_monthly_summary(
    family_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly income summary
    - Require auth
    
    Query params:
    - family_id: filter by family (optional)
    - year: year (optional, default current year)
    - month: month (optional, default current month)
    """
    controller = IncomeController()
    return controller.get_monthly_summary(
        db=db,
        family_id=family_id,
        year=year,
        month=month
    )
