from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.family_mutation import FamilyMutationController
from app.controllers.dependencies import get_db, get_current_user, require_role
from app.schemas.family_mutation import (
    FamilyMutationCreate,
    FamilyMutationResponse,
    FamilyMutationListResponse,
)
from app.models.user import User


router = APIRouter(prefix="/family-mutations", tags=["family-mutations"])


@router.get("", response_model=List[FamilyMutationListResponse])
def list_mutations(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    controller = FamilyMutationController(db)
    muts = controller.list_mutations(skip=skip, limit=limit)
    response = []
    for m in muts:
        response.append({
            'id': m.id,
            'family_id': m.family_id,
            'family_number': getattr(m.family, 'family_number', None),
            'mutation_type': getattr(m, 'mutation_type', None),
            'description': getattr(m, 'description', None),
            'alamat_lama': getattr(m, 'alamat_lama', None),
            'alamat_baru': getattr(m, 'alamat_baru', None),
            'created_at': m.created_at,
        })
    return response


@router.get("/{mutation_id}", response_model=FamilyMutationResponse)
def get_mutation(mutation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    controller = FamilyMutationController(db)
    m = controller.get_mutation(mutation_id)
    return {
        'id': m.id,
        'family_id': m.family_id,
        'family_number': getattr(m.family, 'family_number', None),
        'mutation_type': getattr(m, 'mutation_type', None),
        'description': getattr(m, 'description', None),
        'alamat_lama': getattr(m, 'alamat_lama', None),
        'alamat_baru': getattr(m, 'alamat_baru', None),
        'created_at': m.created_at,
    }


@router.post("", response_model=FamilyMutationResponse, status_code=status.HTTP_201_CREATED)
def create_mutation(data: FamilyMutationCreate, current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")), db: Session = Depends(get_db)):
    controller = FamilyMutationController(db)
    return controller.create_mutation(data)


@router.delete("/{mutation_id}")
def delete_mutation(mutation_id: int, current_user: User = Depends(require_role("admin", "ketua_rt", "ketua_rw")), db: Session = Depends(get_db)):
    controller = FamilyMutationController(db)
    return controller.delete_mutation(mutation_id)
