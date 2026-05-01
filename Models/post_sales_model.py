from extensions import db
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.orders_id'), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    #columns for Razorpay
    razorpay_order_id = db.Column(db.String(255), unique=True) # ID generated before payment
    razorpay_payment_id = db.Column(db.String(255), unique=True) # ID generated after successful payment
    razorpay_signature = db.Column(db.String(255)) # For security verification
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, completed, failed, refunded
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoice'
    invoice_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.orders_id'), unique=True)
    invoice_number = db.Column(db.String(255), unique=True)
    pdf_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'
    order_tracking_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.orders_id'))
    status = db.Column(db.String(50))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    wishlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))

class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)