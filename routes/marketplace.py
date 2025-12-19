from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.controllers.marketplace import MarketplaceController
from app.controllers.dependencies import get_db, get_current_user
from app.schemas.marketplace import (
    MarketplaceProductCreate,
    MarketplaceProductUpdate,
    MarketplaceProductResponse,
    MarketplaceOrderCreate,
    MarketplaceOrderResponse,
    VerificationRequest,
    VerificationResponse,
)
from app.models.user import User
from app.controllers.prediction import PredictionController
from typing import List
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def format_product(product):
    """Format product response with camelCase field names for Flutter"""
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price) if product.price else 0.0,
        "quantity": product.stock or 0,
        "unit": "piece",
        "imagePath": product.image or "",
        "status": product.status,
        "createdAt": product.created_at.isoformat() if product.created_at else None,
        "sellerName": product.resident.name if product.resident else None,
        "sellerPhone": product.resident.phone if product.resident else None,
        "residentId": product.resident_id,
        "verificationResultId": product.verification_id,
    }


# ============= PRODUCTS ENDPOINTS =============

@router.post("/upload-image", response_model=dict)
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload gambar produk ke server
    
    **Returns:**
    - image_url: URL gambar yang sudah diupload
    """
    try:
        # Validasi tipe file berdasarkan extension (lebih reliable)
        allowed_extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
        file_ext = Path(file.filename).suffix
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Hanya file gambar (jpg/png) yang diperbolehkan. File Anda: {file_ext}"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext.lower()}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return URL
        return {
            "image_url": unique_filename,
            "message": "Gambar berhasil diupload"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal upload gambar: {str(e)}")


@router.get("/products", response_model=List[dict])
async def get_products(
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get semua produk marketplace
    
    **Query Parameters:**
    - status: Filter berdasarkan status (active, sold_out, inactive)
    """
    products = MarketplaceController.get_products(db, status=status)
    return [format_product(p) for p in products]


@router.get("/products/{product_id}", response_model=dict)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get detail produk marketplace"""
    product = MarketplaceController.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    return format_product(product)


@router.post("/products", response_model=dict)
async def create_product(
    body: MarketplaceProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Buat produk marketplace baru (REQUIRES vegetable verification first)
    
    **Request Body:**
    - name: Nama produk
    - description: Deskripsi produk
    - price: Harga produk
    - stock: Stok produk (optional)
    - unit: Satuan (optional, default: piece)
    - image: Path gambar produk (optional)
    
    **Note:**
    Verifikasi otomatis dilakukan saat upload untuk semua user (including admin)
    """
    # Validate: User harus punya resident_id
    if not current_user.resident_id:
        raise HTTPException(
            status_code=403,
            detail="Hanya warga yang terdaftar bisa upload produk. Silakan hubungi admin untuk registrasi sebagai warga."
        )
    
    # Cek apakah sudah ada produk dengan nama sama dari user ini
    existing = MarketplaceController.get_products(db, status=None)
    for prod in existing:
        if prod.resident_id == current_user.resident_id and prod.name.lower() == body.name.lower():
            raise HTTPException(
                status_code=400, 
                detail=f"Anda sudah memiliki produk dengan nama '{body.name}'. Gunakan nama lain atau edit produk yang sudah ada."
            )
    
    # Create product
    product = MarketplaceController.create_product(
        db=db,
        resident_id=current_user.resident_id,
        name=body.name,
        price=body.price,
        description=body.description,
        quantity=body.stock or 0,
        unit=body.unit or "piece",
        image_path=body.image,
        verification_id=None,
    )
    
    return {
        "message": "Produk berhasil dibuat",
        "data": format_product(product)
    }


@router.put("/products/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    quantity: int = None,
    imagePath: str = None,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update produk marketplace"""
    product = MarketplaceController.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    # Check ownership - allow admin to manage all products
    is_admin = current_user.role == "admin" or current_user.role == "admin_sistem"
    if product.resident_id != current_user.resident_id and not is_admin:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki izin untuk mengubah produk ini")
    
    # Cek nama duplikat jika nama diubah
    if name and name.lower() != product.name.lower():
        existing = MarketplaceController.get_products(db, status=None)
        for prod in existing:
            if prod.id != product_id and prod.resident_id == product.resident_id and prod.name.lower() == name.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Anda sudah memiliki produk dengan nama '{name}'. Gunakan nama lain."
                )
    
    updated = MarketplaceController.update_product(
        db=db,
        product_id=product_id,
        name=name,
        price=price,
        description=description,
        image_path=imagePath,
        quantity=quantity,
        status=status,
    )
    
    return format_product(updated)


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete produk marketplace"""
    product = MarketplaceController.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    # Check ownership - allow admin to delete any product
    is_admin = current_user.role == "admin" or current_user.role == "admin_sistem"
    if product.resident_id != current_user.resident_id and not is_admin:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki izin untuk menghapus produk ini")
    
    success = MarketplaceController.delete_product(db, product_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Gagal menghapus produk")
    
    return {"message": "Produk berhasil dihapus"}


# ============= ORDERS ENDPOINTS =============

def format_order(order):
    """Format order response with camelCase field names"""
    return {
        "id": order.id,
        "productId": order.product_id,
        "buyerId": order.buyer_id,
        "productName": order.product.name if order.product else None,
        "quantity": order.quantity,
        "totalPrice": float(order.total_price) if order.total_price else 0.0,
        "status": order.status,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "paymentMethod": "transfer",
    }


@router.get("/orders", response_model=List[dict])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get semua pesanan user (sebagai pembeli)"""
    orders = MarketplaceController.get_orders(db, buyer_id=current_user.id)
    return [format_order(o) for o in orders]


@router.post("/orders", response_model=dict)
async def create_order(
    productId: int,
    quantity: int,
    paymentMethod: str = "transfer",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Buat pesanan marketplace
    
    **Required:**
    - productId: ID produk
    - quantity: Jumlah pembelian
    
    **Optional:**
    - paymentMethod: Metode pembayaran (default: transfer)
    """
    product = MarketplaceController.get_product_by_id(db, productId)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    # Check stock
    if product.stock and product.stock < quantity:
        raise HTTPException(status_code=400, detail="Stok tidak cukup")
    
    order = MarketplaceController.create_order(
        db=db,
        buyer_id=current_user.id,
        product_id=productId,
        quantity=quantity,
        payment_method=paymentMethod,
    )
    
    return format_order(order)


@router.get("/orders/{order_id}", response_model=dict)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detail pesanan"""
    order = MarketplaceController.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    
    # Check ownership
    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke pesanan ini")
    
    return format_order(order)


# ============= VERIFICATION ENDPOINTS =============

@router.post("/verify-vegetable", response_model=dict)
async def verify_vegetable(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verifikasi kualitas sayur menggunakan AI
    
    **Request:**
    - file: Gambar sayur (.jpg, .png, atau .bmp)
    
    **Response:**
    - is_valid: Apakah sayur utuh atau tidak
    - confidence: Tingkat kepercayaan (0-1)
    - vegetable_type: Jenis sayur yang terdeteksi
    - model_version: Versi model yang digunakan
    """
    try:
        # Validasi tipe file
        PredictionController.validate_file(str(file.content_type))
        
        # Baca file contents
        contents = await file.read()
        
        # Validasi ukuran file
        PredictionController.validate_file_size(len(contents))
        
        # Jalankan prediksi
        result = PredictionController.predict(contents, str(file.filename))
        
        # Extract hasil prediksi
        prediction = result.get("data", {}).get("prediction", "Tidak Utuh")
        confidence = result.get("data", {}).get("confidence", 0)
        class_probs = result.get("data", {}).get("class_probabilities", {})
        
        # Debug logging
        print(f"🔍 Prediction result: {result}")
        print(f"🔍 Prediction: {prediction}, Confidence: {confidence}")
        print(f"🔍 Class probabilities: {class_probs}")
        
        return {
            "is_valid": prediction == "Utuh",
            "confidence": float(confidence),
            "vegetable_type": "Sayur/Buah",  # Generic type since model only checks integrity
            "model_version": "mobilenetv2",
        }
    except Exception as e:
        import traceback
        print(f"❌ Verification error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Verifikasi gagal: {str(e)}")


# ============= BACKWARD COMPATIBILITY =============

@router.post("/vegetable-verification", response_model=dict)
async def vegetable_verification(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alias untuk /marketplace/verify-vegetable (backward compatibility)"""
    return await verify_vegetable(file, current_user, db)

