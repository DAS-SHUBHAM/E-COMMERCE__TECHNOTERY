import os
import json
import uuid  # Added to generate unique IDs
from werkzeug.utils import secure_filename
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from Models.product_models import Product, SellerCategory, ProductImage, Specification

# Define allowed image types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@jwt_required()
def add_product_fn():
    claims = get_jwt()
    # Check if user is a seller (role_id 2)
    if claims.get('role') != 2: 
        return jsonify({"message": "Only sellers can add products"}), 403

    seller_id = int(get_jwt_identity())
    
    # 1. READ TEXT DATA FROM FORM
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')
    category_id = request.form.get('category_id')

    # Security check: ensure category is approved for this seller
    approval_check = SellerCategory.query.filter_by(
        seller_id=seller_id, 
        category_id=category_id, 
        is_approved=True, 
        is_active=True
    ).first()

    if not approval_check:
        return jsonify({"message": "Access Denied! You are not approved for this category."}), 403

    try:
        # A. ENTRY IN PRODUCT TABLE
        new_product = Product(
            uuid=str(uuid.uuid4()), # Generate UUID if not handled by DB default
            name=name,
            description=description,
            price=float(price),
            stock=int(stock),
            category_id=int(category_id),
            seller_id=seller_id,
            is_active=True
        )
        db.session.add(new_product)
        db.session.flush() # Generate product_id for child tables

        # B. ENTRY IN SPECIFICATION TABLE
        spec_string = request.form.get('specification', '[]')
        specifications = json.loads(spec_string) 
        
        for spec in specifications:
            # FIX: Ensure these match your database column names exactly
            # and use the same keys you send in Postman
            new_spec = Specification(
                product_id=new_product.product_id, 
                spec_key=spec.get('spec_key'),   
                spec_value=spec.get('spec_value') 
            )
            db.session.add(new_spec)

        # C. ENTRY IN PRODUCT IMAGES TABLE
        images = request.files.getlist('images')
        
        # Automatic folder creation
        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True) 

        for index, file in enumerate(images):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"prod_{new_product.product_id}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                # Save physical file
                file.save(file_path)

                # Save relative path for frontend access
                db_image_url = f"/static/uploads/products/{unique_filename}"
                
                new_image = ProductImage(
                    product_id=new_product.product_id,
                    image_url=db_image_url,
                    is_primary=(index == 0) 
                )
                db.session.add(new_image)

        db.session.commit()

        return jsonify({
            "message": "Product added successfully with local images!",
            "product_uuid": new_product.uuid
        }), 201

    except Exception as e:
        db.session.rollback()
        # Returns the specific error for debugging
        return jsonify({"message": "Failed to add product", "error": str(e)}), 500