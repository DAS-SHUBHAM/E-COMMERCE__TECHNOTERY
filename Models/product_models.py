from extensions import db
from datetime import datetime
import uuid

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True) 
    updated_by = db.Column(db.Integer, nullable=True)

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
    # ADDED: is_approved column with default=True
    # This ensures that if the category is already seller-approved, 
    # the product becomes visible immediately.
    is_approved = db.Column(db.Boolean, default=True) 
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    product_image_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

class Specification(db.Model):
    __tablename__ = 'specification'
    specification_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    spec_key = db.Column(db.String(255), nullable=False)
    spec_value = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class SellerCategory(db.Model):
    __tablename__ = 'seller_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, nullable=True) 
    updated_by = db.Column(db.Integer, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('seller_id', 'category_id', name='_seller_category_uc'),)