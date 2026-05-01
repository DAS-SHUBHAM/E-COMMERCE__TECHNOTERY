from extensions import db
from datetime import datetime
import uuid

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True) # Soft delete for cart management
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Orders(db.Model):
    __tablename__ = 'orders'
    orders_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    # Payment methods handled as strings: cod, card, upi, etc.
    payment_method = db.Column(db.String(50)) 
    # Order lifecycle status: pending, processing, shipped, delivered, cancelled
    status = db.Column(db.String(50), default='pending') 
    is_active = db.Column(db.Boolean, default=True) # Tracks if the overall order is valid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    order_item_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.orders_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Store price at the time of purchase to maintain history if product price changes later
    price_at_purchase = db.Column(db.Float, nullable=False) 
    is_active = db.Column(db.Boolean, default=True) # Individual item cancellation status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)