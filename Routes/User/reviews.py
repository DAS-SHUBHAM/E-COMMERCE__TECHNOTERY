from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime

# Import models
from Models.post_sales_model import Review
from Models.product_models import Product
from Models.user_models import User

@jwt_required()
def add_review_fn(product_id):
    """
    To add a review to a product: if the user has already given a review, it will be updated.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    rating = data.get('rating')
    comment = data.get('comment')

    # Validation: Rating should be in between 1 to 5
    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({"message": "Please provide a valid rating between 1 and 5"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    # Check if review already exists for this user and product
    existing_review = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing_review:
        # Update old review
        existing_review.rating = int(rating)
        existing_review.comment = comment
        existing_review.created_at = datetime.utcnow() # Update timestamp
        message = "Review updated successfully"
    else:
        # Create new review
        new_review = Review(
            user_id=user_id,
            product_id=product_id,
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


def get_product_reviews_fn(product_id):
    """
    Kisi product ke saare reviews dekhne ke liye (Bina login kiye).
    """
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    if not reviews:
        return jsonify({"message": "No reviews yet for this product", "reviews": []}), 200
        
    review_data = []
    total_rating = 0
    
    for r in reviews:
        user = User.query.get(r.user_id)
        review_data.append({
            "review_id": r.review_id,
            "username": user.username if user else "Unknown User",
            "rating": r.rating,
            "comment": r.comment,
            "date": r.created_at.strftime("%d %B, %Y") # e.g. 01 May, 2026
        })
        total_rating += r.rating
        
    # Calculate Average Rating
    avg_rating = round(total_rating / len(reviews), 1)

    return jsonify({
        "product_name": product.name,
        "average_rating": avg_rating,
        "total_reviews": len(reviews),
        "reviews": review_data
    }), 200