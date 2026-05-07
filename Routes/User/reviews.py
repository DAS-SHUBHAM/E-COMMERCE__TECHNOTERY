from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime
import uuid
from Models.post_sales_model import Review
from Models.product_models import Product
from Models.user_models import User

@jwt_required()
def add_review_fn(product_uuid): # Updated to product_uuid
    user_id = get_jwt_identity()
    data = request.get_json()
    
    rating = data.get('rating')
    comment = data.get('comment')

    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({"message": "Please provide a valid rating between 1 and 5"}), 400

    # Product ko UUID se dhundein
    product = Product.query.filter_by(uuid=product_uuid).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    existing_review = Review.query.filter_by(user_id=user_id, product_id=product.product_id).first()
    
    if existing_review:
        existing_review.rating = int(rating)
        existing_review.comment = comment
        existing_review.created_at = datetime.utcnow()
        message = "Review updated successfully"
    else:
        new_review = Review(
            uuid=str(uuid.uuid4()), # Naya UUID assign kiya
            user_id=user_id,
            product_id=product.product_id,
            rating=int(rating),
            comment=comment
        )
        db.session.add(new_review)
        message = "Review submitted successfully"
        
    try:
        db.session.commit()
        return jsonify({"message": message}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error saving review", "error": str(e)}), 500


def get_product_reviews_fn(product_uuid): # Updated to product_uuid
    product = Product.query.filter_by(uuid=product_uuid).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    reviews = Review.query.filter_by(product_id=product.product_id).order_by(Review.created_at.desc()).all()
    
    if not reviews:
        return jsonify({"message": "No reviews yet for this product", "reviews": []}), 200
        
    review_data = []
    total_rating = 0
    
    for r in reviews:
        user = User.query.get(r.user_id)
        review_data.append({
            "review_uuid": r.uuid, # Ab review_id ki jagah uuid bhejenge
            "username": user.username if user else "Unknown User",
            "rating": r.rating,
            "comment": r.comment,
            "date": r.created_at.strftime("%d %B, %Y")
        })
        total_rating += r.rating
        
    avg_rating = round(total_rating / len(reviews), 1)

    return jsonify({
        "product_name": product.name,
        "average_rating": avg_rating,
        "total_reviews": len(reviews),
        "reviews": review_data
    }), 200