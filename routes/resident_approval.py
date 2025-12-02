from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers.resident_approval import ResidentApprovalController
from app.controllers.dependencies import get_db, get_current_user
from app.schemas.resident_approval import (
    ResidentApprovalUpdate,
    ResidentApprovalResponse,
    ResidentApprovalListResponse
)
from app.models.user import User
from typing import List


router = APIRouter(prefix="/resident-approvals", tags=["resident-approvals"])


@router.get("", response_model=List[ResidentApprovalListResponse])
def list_resident_approvals(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List resident approvals
    - Require auth (rt/rw/admin)
    - Filter by status (pending_approval, approved, rejected)
    
    Query params:
    - status: pending_approval | approved | rejected
    - skip: offset
    - limit: max results (default 100)
    """
    controller = ResidentApprovalController(db)
    return controller.list_approvals(status_filter=status, skip=skip, limit=limit)


@router.get("/{approval_id}", response_model=ResidentApprovalResponse)
def get_resident_approval(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single resident approval by ID"""
    controller = ResidentApprovalController(db)
    return controller.get_approval(approval_id)


@router.put("/{approval_id}", response_model=ResidentApprovalResponse)
def update_resident_approval(
    approval_id: int,
    data: ResidentApprovalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject resident registration
    - Require auth (rt/rw/admin)
    - Update resident status + family_id (if approved)
    - Update approval status + note
    
    Request body:
    {
      "status": "approved" | "rejected",
      "note": "Optional note (only for rejection)",
      "family_id": 5  (optional - if not provided, will auto-create family + set as head_resident)
    }
    
    Flow:
    1. If status="approved" + family_id provided: assign to existing family
    2. If status="approved" + family_id NOT provided: auto-create family from family_number + set as head_resident
    3. If status="rejected": reject registration
    """
    controller = ResidentApprovalController(db)
    
    if data.status == "approved":
        return controller.approve_resident(approval_id, data, current_user)
    elif data.status == "rejected":
        return controller.reject_resident(approval_id, data, current_user)
