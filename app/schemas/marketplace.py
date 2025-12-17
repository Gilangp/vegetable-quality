from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MarketplaceProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int = 0
    unit: str = "piece"


class MarketplaceProductCreate(MarketplaceProductBase):
    stock: Optional[int] = None  # Flutter sends 'stock', not 'quantity'
    image: Optional[str] = None  # Flutter sends 'image', not 'image_path'
    verification_id: Optional[int] = None


class MarketplaceProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    image_path: Optional[str] = None
    status: Optional[str] = None


class MarketplaceProductResponse(MarketplaceProductBase):
    id: int
    resident_id: int
    image_path: Optional[str] = None
    status: str
    created_at: datetime
    seller_name: Optional[str] = None
    seller_phone: Optional[str] = None

    class Config:
        from_attributes = True


class MarketplaceOrderCreate(BaseModel):
    product_id: int
    quantity: int
    payment_method: str = "transfer"


class MarketplaceOrderResponse(BaseModel):
    id: int
    buyer_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class VerificationRequest(BaseModel):
    image_path: str
    vegetable_name: Optional[str] = None


class VerificationResponse(BaseModel):
    is_valid: bool
    confidence: float
    vegetable_type: str
    model_version: str = "mobilenetv2"
