import os
import json
import uuid
from werkzeug.utils import secure_filename
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Product, SellerCategory, ProductImage, Specification
from datetime import datetime

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@jwt_required()
def add_product_fn():
    """
    Seller-only API to add a new product. 
    Includes strict validation for price, stock, category approval, and image uploads.
    """
    claims = get_jwt()
    
    # 1. Role Validation: Ensure the user is a Seller (Role 2)
    if claims.get('role') != 2: 
        return jsonify({"message": "Access Denied! Only sellers can list products."}), 403

    seller_id = int(get_jwt_identity())
    
    # 2. Extract Form Data
    name = request.form.get('name')
    description = request.form.get('description')
    price_raw = request.form.get('price')
    stock_raw = request.form.get('stock')
    category_id_raw = request.form.get('category_id')

    # 3. Mandatory Fields Validation: Check if any required field is empty
    if not all([name, price_raw, stock_raw, category_id_raw]):
        return jsonify({"message": "Missing required fields: name, price, stock, and category_id are mandatory."}), 400

    # 4. Numerical Validations (Price and Stock)
    try:
        price = float(price_raw)
        stock = int(stock_raw)
        category_id = int(category_id_raw)

        # Logical Check: Price cannot be zero or negative
        if price <= 0:
            return jsonify({"message": "Invalid Price! Price must be a positive number greater than zero."}), 400
        
        # Logical Check: Stock cannot be negative
        if stock < 0:
            return jsonify({"message": "Invalid Stock! Stock cannot be a negative value."}), 400

    except ValueError:
        return jsonify({"message": "Data Type Error! Price must be a decimal and Stock/Category must be integers."}), 400

    # 5. Security Check: Verify if the seller is approved for this specific category
    approval_check = SellerCategory.query.filter_by(
        seller_id=seller_id, 
        category_id=category_id, 
        is_approved=True, 
        is_active=True
    ).first()

    if not approval_check:
        return jsonify({"message": "Unauthorized Category! You are not approved to sell products in this category."}), 403

    try:
        # A. Create Product Entry
        new_product = Product(
            uuid=str(uuid.uuid4()),
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            seller_id=seller_id,
            is_active=True
        )
        db.session.add(new_product)
        db.session.flush() # Flush to get new_product.product_id

        # B. Handle Specifications (JSON Validation)
        spec_string = request.form.get('specification', '[]')
        try:
            specifications = json.loads(spec_string)
        except json.JSONDecodeError:
            return jsonify({"message": "Format Error! Specifications must be a valid JSON string."}), 400
        
        for spec in specifications:
            new_spec = Specification(
                product_id=new_product.product_id, 
                spec_key=spec.get('spec_key'),   
                spec_value=spec.get('spec_value') 
            )
            db.session.add(new_spec)

        # C. Handle Image Uploads
        images = request.files.getlist('images')
        if not images or len(images) == 0:
            return jsonify({"message": "Product images are required. Please upload at least one image."}), 400

        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True) 

        for index, file in enumerate(images):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create a unique filename to avoid overwriting
                unique_filename = f"prod_{new_product.product_id}_{uuid.uuid4().hex[:8]}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                file.save(file_path)

                # Store relative URL for database
                db_image_url = f"/static/uploads/products/{unique_filename}"
                
                new_image = ProductImage(
                    product_id=new_product.product_id,
                    image_url=db_image_url,
                    is_primary=(index == 0) # First image is set as primary
                )
                db.session.add(new_image)

        # Final Database Commit
        db.session.commit()

        return jsonify({
            "message": "Product added successfully with all details and images!",
            "product_uuid": new_product.uuid
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Transaction Failed! Product could not be added.",
            "error": str(e)
        }), 500