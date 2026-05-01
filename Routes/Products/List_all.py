from flask import jsonify
from Models.product_models import Product
from Models.user_models import User
from extensions import db
from sqlalchemy import desc # Naya product top par dikhane ke liye

def list_all_fn():
    # 1. Query with Join: Fetch products and seller usernames
    # Added .order_by(desc(Product.product_id)) so newest products appear FIRST
    query = db.session.query(Product, User.username).join(
        User, Product.seller_id == User.user_id
    )

    # 2. Filter: Only show products that are active and approved
    # Since we set default=True in the model, new products will show up immediately
    products = query.filter(
        Product.is_active == True, 
        Product.is_approved == True
    ).order_by(desc(Product.product_id)).all()

    # 3. Format the response
    return jsonify([{
        "uuid": p.Product.uuid,
        "name": p.Product.name,
        "price": p.Product.price,
        "seller": p.username,
        "is_approved": p.Product.is_approved, # Reference ke liye add kiya hai
        "stock_status": "In Stock" if p.Product.stock > 0 else "Out of Stock"
    } for p in products]), 200