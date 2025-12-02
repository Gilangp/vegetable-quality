from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers.family import FamilyController
from app.controllers.dependencies import get_db, get_current_user
from app.schemas.family import (
    FamilyCreate,
    FamilyUpdate,
    FamilyResponse,
    FamilyListResponse,
    ResidentInFamily
)
from app.models.user import User
from typing import List


router = APIRouter(prefix="/families", tags=["families"])


@router.get("", response_model=List[FamilyListResponse])
def list_families(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all families
    - Require auth
    
    Query params:
    - skip: offset (default 0)
    - limit: max results (default 100)
    """
    controller = FamilyController(db)
    families = controller.list_families(skip=skip, limit=limit)
    
    # Convert to response model with resident_count
    response = []
    for family in families:
        response.append({
            "id": family.id,
            "family_number": family.family_number,
            "head_resident_id": family.head_resident_id,
            "resident_count": len(family.residents) if family.residents else 0,
            "created_at": family.created_at,
            "updated_at": family.updated_at
        })
    
    return response


@router.get("/{family_id}", response_model=FamilyResponse)
def get_family(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single family by ID with members"""
    controller = FamilyController(db)
    return controller.get_family(family_id)


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    data: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new family
    - Require auth (admin/rt/rw)
    
    Request body:
    {
      "family_number": "001",
      "head_resident_id": 1  (optional)
    }
    """
    controller = FamilyController(db)
    return controller.create_family(data)


@router.put("/{family_id}", response_model=FamilyResponse)
def update_family(
    family_id: int,
    data: FamilyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update family
    - Require auth (admin/rt/rw)
    
    Request body:
    {
      "family_number": "001-A",  (optional)
      "head_resident_id": 2      (optional)
    }
    """
    controller = FamilyController(db)
    return controller.update_family(family_id, data)


@router.delete("/{family_id}")
def delete_family(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete family
    - Require auth (admin/rt/rw)
    - Only if no residents
    """
    controller = FamilyController(db)
    return controller.delete_family(family_id)


@router.post("/{family_id}/members/{resident_id}", response_model=ResidentInFamily)
def add_resident_to_family(
    family_id: int,
    resident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add resident to family
    - Require auth (admin/rt/rw)
    """
    controller = FamilyController(db)
    return controller.add_resident_to_family(family_id, resident_id)


@router.delete("/{family_id}/members/{resident_id}")
def remove_resident_from_family(
    family_id: int,
    resident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove resident from family
    - Require auth (admin/rt/rw)
    - Cannot remove if head of family
    """
    controller = FamilyController(db)
    return controller.remove_resident_from_family(family_id, resident_id)
