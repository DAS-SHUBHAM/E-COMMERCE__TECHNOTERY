from flask import jsonify
from extensions import db
from Models.product_models import Product, ProductImage

# No need of JWT because user can view products whithout logging in

def get_all_public_products_fn():
    # Fetching those products which are active 
    products = Product.query.filter_by(is_active=True).all()
    
    response_data = []
    for prod in products:
        # Har product ki sirf Primary image (Thumbnail) fetch karein
        primary_img = ProductImage.query.filter_by(
            product_id=prod.product_id, 
            is_primary=True, 
            is_active=True
        ).first()
        
        response_data.append({
            "uuid": prod.uuid,
            "name": prod.name,
            "price": prod.price,
            "thumbnail": primary_img.image_url if primary_img else None,
            "stock":prod.stock
        })
        
    return jsonify({
        "message": "Products fetched successfully",
        "total_products": len(response_data),
        "products": response_data
    }), 200