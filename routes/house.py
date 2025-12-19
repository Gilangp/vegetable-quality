from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session

from app.controllers.house import HouseController
from app.controllers.dependencies import get_db, get_current_user, require_role
from app.schemas.house import HouseCreate, HouseResponse, HouseUpdate
from app.schemas.residents import ResidentResponse
from app.models.user import User


router = APIRouter(prefix="/houses", tags=["houses"])


@router.get("", response_model=List[HouseResponse])
def list_houses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    controller = HouseController(db)
    houses = controller.list_houses(skip=skip, limit=limit)
    # Convert to response dicts to ensure resident_count present
    response = []
    for h in houses:
        response.append({
            "id": h.id,
            "house_number": h.house_number,
            "address": h.address,
            "rt": h.rt,
            "rw": h.rw,
            "status": getattr(h, 'status', 'available'),
            "resident_count": len(h.residents) if h.residents else 0,
            "created_at": h.created_at,
            "updated_at": h.updated_at,
        })
    return response


@router.get("/{house_id}", response_model=HouseResponse)
def get_house(house_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    controller = HouseController(db)
    return controller.get_house(house_id)


@router.post("", response_model=HouseResponse, status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "House created",
                     "content": {
                         "application/json": {
                             "example": {
                                 "id": 1,
                                 "house_number": "A-101",
                                 "address": "Jl. Mawar No.1",
                                 "rt": "001",
                                 "rw": "002",
                                 "resident_count": 0,
                                 "created_at": "2025-12-04T12:00:00",
                                 "updated_at": "2025-12-04T12:00:00"
                             }
                         }
                     }
                 }
             })
def create_house(
    data: HouseCreate = Body(
        ...,
        example={
            "house_number": "A-101",
            "address": "Jl. Mawar No.1",
            "rt": "001",
            "rw": "002",
        },
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "ketua_rt")),
):
    """Create a new house.

    Body example is provided for Swagger/OpenAPI UI.
    """
    controller = HouseController(db)
    return controller.create_house(data)


@router.put("/{house_id}", response_model=HouseResponse)
def update_house(
    house_id: int,
    data: HouseUpdate = Body(
        ...,
        example={
            "house_number": "A-101",
            "address": "Jl. Mawar No.1",
            "rt": "001",
            "rw": "002",
        },
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "ketua_rt")),
):
    """Update a house. Body example provided for Swagger."""
    controller = HouseController(db)
    return controller.update_house(house_id, data)


@router.delete("/{house_id}")
def delete_house(house_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "ketua_rt"))):
    controller = HouseController(db)
    return controller.delete_house(house_id)


@router.post("/{house_id}/assign/{resident_id}", response_model=ResidentResponse)
def assign_house(house_id: int, resident_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "ketua_rt"))):
    controller = HouseController(db)
    return controller.assign_resident_to_house(house_id, resident_id)
