import os
import zipfile
import csv
import uuid
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

# Direct structural database layer and relational model imports
from extensions import db
from Models.product_models import Product, ProductImage, SellerCategory, Specification
# NOTE: Apne system ke mutabik User ya Seller model ko yahan import kar lijiye jahan uuid store hoti hai
from Models.user_models import User  # Example import, change as per your model filename

# Root workspace directory for raw processing chunks
UPLOAD_DIR = os.path.join(os.getcwd(), 'static', 'uploads', 'bulk_temp')
BASE_PRODUCT_DIR = os.path.join(os.getcwd(), 'static', 'uploads', 'products')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BASE_PRODUCT_DIR, exist_ok=True)

@jwt_required()
def bulk_upload_products_fn():
    """
    Processes multi-part bulk apparel catalogs and dynamically distributes 
    extracted media assets into a strictly isolated hierarchical file system
    based on the Seller's UUID:
    static/uploads/products/seller_<seller_uuid>/product_<uuid>/<image_uuid>.<ext>
    """
    try:
        current_seller_id = get_jwt_identity()

        # 1. Fetch Seller's UUID from Database to prevent exposing integer sequential IDs
        # Sahi user_id column tracking map
        seller_user = User.query.filter_by(user_id=int(current_seller_id)).first()
        if not seller_user or not hasattr(seller_user, 'uuid'):
            return jsonify({"message": "Security Error: Seller verification failed or UUID not found in account system."}), 404
        
        seller_uuid_token = str(seller_user.uuid)

        if 'csv_file' not in request.files or 'zip_file' not in request.files:
            return jsonify({"message": "Payload verification failed. Both 'csv_file' and 'zip_file' parts are mandatory."}), 400
            
        csv_file = request.files['csv_file']
        zip_file = request.files['zip_file']
        
        if csv_file.filename == '' or zip_file.filename == '':
            return jsonify({"message": "Selection error. File streams cannot be initialized with empty file names."}), 400

        secure_csv_name = secure_filename(csv_file.filename)
        secure_zip_name = secure_filename(zip_file.filename)
        
        csv_path = os.path.join(UPLOAD_DIR, secure_csv_name)
        zip_path = os.path.join(UPLOAD_DIR, secure_zip_name)
        
        csv_file.save(csv_path)
        zip_file.save(zip_path)

        extraction_scope_dir = os.path.join(UPLOAD_DIR, f"extracted_{secure_zip_name.split('.')[0]}")
        os.makedirs(extraction_scope_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as archive_ref:
            archive_ref.extractall(extraction_scope_dir)

        products_pipeline = []
        parsing_exceptions = []

        # --- UPGRADED: Folder is now created using seller_uuid_token instead of integer id ---
        seller_directory_path = os.path.join(BASE_PRODUCT_DIR, f"seller_{seller_uuid_token}")
        os.makedirs(seller_directory_path, exist_ok=True)

        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for index, row in enumerate(reader):
                sku_token = str(row.get('sku', '')).strip()
                title_name = row.get('title')
                
                try:
                    price = float(row.get('price', 0)) if row.get('price') else 0.0
                    stock = int(row.get('stock', 0)) if row.get('stock') else 0
                    category_id = int(row.get('category_id', 1)) if row.get('category_id') else 1
                except ValueError as cast_err:
                    parsing_exceptions.append(f"Row {index + 1}: Data numerical transformation fault ({str(cast_err)}).")
                    continue

                if not sku_token or sku_token.lower() == "nan" or sku_token == "":
                    parsing_exceptions.append(f"Row {index + 1}: Data missing critical structural SKU tracking identifier.")
                    continue

                # Security Pass Check: Category Permits
                approval_check = SellerCategory.query.filter_by(
                    seller_id=current_seller_id,
                    category_id=category_id,
                    is_approved=True,
                    is_active=True
                ).first()

                if not approval_check:
                    parsing_exceptions.append(f"Row {index + 1}: Security Restriction. Active merchant permit missing for category_id '{category_id}'.")
                    continue

                if Product.query.filter_by(sku=sku_token).first():
                    parsing_exceptions.append(f"Row {index + 1}: SKU identifier token '{sku_token}' already registered inside system catalog.")
                    continue

                # Multi-Image Array Discovery
                matched_images = []
                for extracted_file in os.listdir(extraction_scope_dir):
                    if extracted_file.lower().startswith(sku_token.lower()):
                        matched_images.append(extracted_file)

                if not matched_images:
                    parsing_exceptions.append(f"Row {index + 1}: Asset tracking fault. No images found for SKU '{sku_token}' inside ZIP.")
                    continue

                matched_images.sort()

                # Generate Product Entity Node and Pre-bind its unique tracking UUID
                product_uuid_token = str(uuid.uuid4())
                new_product_node = Product(
                    uuid=product_uuid_token,
                    sku=sku_token,
                    name=title_name,
                    price=price,
                    description=row.get('description', ''),
                    stock=stock,
                    category_id=category_id,
                    is_approved=False,
                    seller_id=current_seller_id
                )
                
                # Setup Product Isolated Sub-directory Layout under Seller Context
                product_directory_path = os.path.join(seller_directory_path, f"product_{product_uuid_token}")
                os.makedirs(product_directory_path, exist_ok=True)

                # Dynamic Specifications Append Loop
                specifications_map = {
                    "Size": row.get('spec_size'),
                    "Color": row.get('spec_color'),
                    "Material": row.get('spec_material')
                }

                for key, value in specifications_map.items():
                    if value and str(value).strip() != "" and str(value).lower() != "nan":
                        spec_node = Specification(
                            spec_key=key,
                            spec_value=str(value).strip(),
                            is_active=True
                        )
                        new_product_node.specifications.append(spec_node)

                # Process and Rename Matched Assets with structural image UUIDs
                for img_index, img_filename in enumerate(matched_images):
                    source_image_path = os.path.join(extraction_scope_dir, img_filename)
                    
                    file_extension = os.path.splitext(img_filename)[1].lower()
                    if not file_extension:
                        file_extension = '.jpg'
                    
                    image_uuid_token = str(uuid.uuid4())
                    is_primary_flag = True if img_index == 0 else False

                    final_filename = f"{image_uuid_token}{file_extension}"
                    destination_image_path = os.path.join(product_directory_path, final_filename)

                    os.rename(source_image_path, destination_image_path)
                    
                    # --- UPGRADED: Web URL routing now accurately reflects the seller's UUID ---
                    public_serving_url = f"/static/uploads/products/seller_{seller_uuid_token}/product_{product_uuid_token}/{final_filename}"

                    product_image_node = ProductImage(
                        uuid=image_uuid_token,
                        image_url=public_serving_url,
                        is_primary=is_primary_flag,
                        is_active=True
                    )
                    new_product_node.images.append(product_image_node)
                
                products_pipeline.append(new_product_node)

        if products_pipeline:
            db.session.add_all(products_pipeline)
            db.session.commit()

        # Garbage Collection Purge Block
        if os.path.exists(csv_path): os.remove(csv_path)
        if os.path.exists(zip_path): os.remove(zip_path)
        for root, dirs, files in os.walk(extraction_scope_dir, topdown=False):
            for file in files: os.remove(os.path.join(root, file))
            for directory in dirs: os.rmdir(os.path.join(root, directory))
        os.rmdir(extraction_scope_dir)

        return jsonify({
            "message": f"Bulk Ingestion Engine successfully fully uploaded {len(products_pipeline)} records into secure nested Seller UUID storage matrix.",
            "unprocessed_log_exceptions": parsing_exceptions
        }), 200

    except Exception as general_exception:
        db.session.rollback()
        return jsonify({"message": "Critical structural failure encountered during asset routing.", "error": str(general_exception)}), 500