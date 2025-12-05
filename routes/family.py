from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.family import FamilyController
from app.controllers.dependencies import get_db, get_current_user, require_role
from app.schemas.family import (
    FamilyCreate,
    FamilyResponse,
    FamilyListResponse,
    FamilyUpdate,
    ResidentInFamily,
    MessageResponse,
)
from app.models.user import User


router = APIRouter(prefix="/families", tags=["families"])


@router.get("", response_model=List[FamilyListResponse])
def list_families(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all families (requires authentication).

    Query params:
    - skip: offset (default 0)
    - limit: max results (default 100)
    """
    controller = FamilyController(db)
    families = controller.list_families(skip=skip, limit=limit)

    # Convert to response model with resident_count
    response = []
    for family in families:
        response.append(
            {
                "id": family.id,
                "family_number": family.family_number,
                "head_resident_id": family.head_resident_id,
                "resident_count": len(family.residents) if family.residents else 0,
                "head_resident": {
                    "id": family.head_resident.id,
                    "name": family.head_resident.name,
                    "nik": getattr(family.head_resident, 'nik', None),
                    "gender": getattr(family.head_resident, 'gender', None),
                    "status": getattr(family.head_resident, 'status', None),
                    "house_id": getattr(family.head_resident, 'house_id', None),
                } if family.head_resident is not None else None,
                "created_at": family.created_at,
                "updated_at": family.updated_at,
            }
        )

    return response


@router.get("/{family_id}", response_model=FamilyResponse)
def get_family(
    family_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get single family by ID with members."""
    controller = FamilyController(db)
    return controller.get_family(family_id)


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    data: FamilyCreate,
    current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")),
    db: Session = Depends(get_db),
):
    """Create new family (requires role admin/ketua_rt/ketua_rw)."""
    controller = FamilyController(db)
    return controller.create_family(data)


@router.put("/{family_id}", response_model=FamilyResponse)
def update_family(
    family_id: int,
    data: FamilyUpdate,
    current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")),
    db: Session = Depends(get_db),
):
    """Update family details (requires role admin/ketua_rt/ketua_rw)."""
    controller = FamilyController(db)
    return controller.update_family(family_id, data)


@router.delete("/{family_id}", response_model=MessageResponse)
def delete_family(
    family_id: int,
    current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")),
    db: Session = Depends(get_db),
):
    """Delete family (only allowed if no residents)."""
    controller = FamilyController(db)
    return controller.delete_family(family_id)


@router.post("/{family_id}/members/{resident_id}", response_model=ResidentInFamily)
def add_resident_to_family(
    family_id: int,
    resident_id: int,
    current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")),
    db: Session = Depends(get_db),
):
    """Add resident to family (requires role admin/ketua_rt/ketua_rw)."""
    controller = FamilyController(db)
    resident = controller.add_resident_to_family(family_id, resident_id)

    # Convert related house to plain dict to satisfy response_model expectations
    house_obj = None
    if getattr(resident, 'house', None) is not None:
        h = resident.house
        house_obj = {
            'id': getattr(h, 'id', None),
            'house_number': getattr(h, 'house_number', None),
            'address': getattr(h, 'address', None),
            'rt': getattr(h, 'rt', None),
            'rw': getattr(h, 'rw', None),
            'created_at': getattr(h, 'created_at', None),
            'updated_at': getattr(h, 'updated_at', None),
        }

    response = {
        'id': resident.id,
        'name': resident.name,
        'nik': getattr(resident, 'nik', None),
        'gender': getattr(resident, 'gender', None),
        'status': getattr(resident, 'status', None),
        'house_id': getattr(resident, 'house_id', None),
        'house': house_obj,
    }

    return response


@router.delete("/{family_id}/members/{resident_id}", response_model=ResidentInFamily)
def remove_resident_from_family(
    family_id: int,
    resident_id: int,
    current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")),
    db: Session = Depends(get_db),
):
    """Remove resident from family by setting `family_id` to NULL and
    return the updated resident payload so the client can refresh its UI.
    """
    controller = FamilyController(db)
    resident = controller.remove_resident_from_family(family_id, resident_id)

    # Convert related house to plain dict to satisfy response_model expectations
    house_obj = None
    if getattr(resident, 'house', None) is not None:
        h = resident.house
        house_obj = {
            'id': getattr(h, 'id', None),
            'house_number': getattr(h, 'house_number', None),
            'address': getattr(h, 'address', None),
            'rt': getattr(h, 'rt', None),
            'rw': getattr(h, 'rw', None),
            'created_at': getattr(h, 'created_at', None),
            'updated_at': getattr(h, 'updated_at', None),
        }

    response = {
        'id': resident.id,
        'name': resident.name,
        'nik': getattr(resident, 'nik', None),
        'gender': getattr(resident, 'gender', None),
        'status': getattr(resident, 'status', None),
        'house_id': getattr(resident, 'house_id', None),
        'house': house_obj,
    }

    return response


@router.post("/public", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family_public(
    data: FamilyCreate,
    db: Session = Depends(get_db),
):
    """Create new family WITHOUT role checks (useful for testing/demo).

    This endpoint intentionally does not require authentication. Use with
    caution in production; it is intended to simplify testing via Swagger
    or Postman when a valid user token is not available.
    """
    controller = FamilyController(db)
    return controller.create_family(data)
