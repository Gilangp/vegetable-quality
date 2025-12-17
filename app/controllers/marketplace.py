from sqlalchemy.orm import Session
from app.models.marketplace_product import MarketplaceProduct
from app.models.marketplace_order import MarketplaceOrder
from app.models.resident_model import Resident
from datetime import datetime


class MarketplaceController:
    """Controller untuk mengelola produk marketplace dan pesanan"""

    @staticmethod
    def get_products(db: Session, status: str = None, resident_id: int = None):
        """Get semua produk marketplace dengan filter optional"""
        query = db.query(MarketplaceProduct)
        
        if status:
            query = query.filter(MarketplaceProduct.status == status)
        
        if resident_id:
            query = query.filter(MarketplaceProduct.resident_id == resident_id)
        
        return query.all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int):
        """Get produk marketplace berdasarkan ID"""
        return db.query(MarketplaceProduct).filter(
            MarketplaceProduct.id == product_id
        ).first()

    @staticmethod
    def create_product(
        db: Session,
        resident_id: int,
        name: str,
        price: float,
        description: str,
        image_path: str = None,
        quantity: int = 0,
        unit: str = "piece",
        verification_id: int = None,
    ):
        """Buat produk marketplace baru"""
        product = MarketplaceProduct(
            resident_id=resident_id,
            verification_id=verification_id,
            name=name,
            price=price,
            stock=quantity,
            description=description,
            image=image_path,
            status="active",
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        name: str = None,
        price: float = None,
        description: str = None,
        image_path: str = None,
        quantity: int = None,
        status: str = None,
    ):
        """Update produk marketplace"""
        product = MarketplaceController.get_product_by_id(db, product_id)
        if not product:
            return None
        
        if name:
            product.name = name
        if price:
            product.price = price
        if description:
            product.description = description
        if image_path:
            product.image = image_path
        if quantity is not None:
            product.stock = quantity
        if status:
            product.status = status
        
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        """Delete produk marketplace"""
        product = MarketplaceController.get_product_by_id(db, product_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True

    @staticmethod
    def create_order(
        db: Session,
        buyer_id: int,
        product_id: int,
        quantity: int,
        payment_method: str = "transfer",
    ):
        """Buat pesanan marketplace"""
        product = MarketplaceController.get_product_by_id(db, product_id)
        if not product:
            return None
        
        # Calculate total price
        total_price = product.price * quantity
        
        order = MarketplaceOrder(
            buyer_id=buyer_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            status="pending",
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_orders(db: Session, buyer_id: int = None, seller_id: int = None):
        """Get pesanan dengan filter optional"""
        query = db.query(MarketplaceOrder)
        
        if buyer_id:
            query = query.filter(MarketplaceOrder.buyer_id == buyer_id)
        
        if seller_id:
            # Join dengan product untuk filter berdasarkan seller
            query = query.join(MarketplaceProduct).filter(
                MarketplaceProduct.resident_id == seller_id
            )
        
        return query.all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int):
        """Get pesanan berdasarkan ID"""
        return db.query(MarketplaceOrder).filter(
            MarketplaceOrder.id == order_id
        ).first()

    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str):
        """Update status pesanan"""
        order = MarketplaceController.get_order_by_id(db, order_id)
        if not order:
            return None
        
        order.status = status
        db.commit()
        db.refresh(order)
        return order
