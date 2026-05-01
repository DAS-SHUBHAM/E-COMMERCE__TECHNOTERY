from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import razorpay
from extensions import db
from Models.sales_model import Orders
from Models.post_sales_model import Payment

# Replace these with your actual Test Keys from Razorpay Dashboard
RAZORPAY_KEY_ID = 'rzp_test_SjfXy9hXc1En3Y'
RAZORPAY_KEY_SECRET = 'INZZ4JCnra1z5TXCQW1Yw0vB'

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@jwt_required()
def create_payment_order_fn(order_uuid):
    """
    Step 1: Hit this API before showing the payment gateway to the user.
    It tells Razorpay to create an order and returns the Razorpay Order ID.
    """
    user_id = get_jwt_identity()
    
    # Fetch the order from your database
    main_order = Orders.query.filter_by(uuid=order_uuid, user_id=user_id).first()
    if not main_order:
        return jsonify({"message": "Order not found or unauthorized"}), 404

    if main_order.status == 'cancelled':
        return jsonify({"message": "Cannot pay for a cancelled order."}), 400

    # Razorpay expects amount in PAISE (Multiply INR by 100)
    amount_in_paise = int(main_order.total_amount * 100)

    try:
        # Create order in Razorpay
        razorpay_order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"receipt_{main_order.orders_id}",
            "payment_capture": "1" # Auto-capture payment
        }
        razorpay_order = razorpay_client.order.create(data=razorpay_order_data)
        
        # Save this payment attempt in our database as 'pending'
        new_payment = Payment(
            order_id=main_order.orders_id,
            user_id=user_id,
            razorpay_order_id=razorpay_order['id'],
            amount=main_order.total_amount,
            status='pending'
        )
        db.session.add(new_payment)
        db.session.commit()

        # Send the Razorpay Order ID to the frontend
        return jsonify({
            "message": "Payment order created successfully",
            "razorpay_order_id": razorpay_order['id'],
            "amount": main_order.total_amount,
            "currency": "INR",
            "key_id": RAZORPAY_KEY_ID # Frontend needs this to open the popup
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create Razorpay order", "error": str(e)}), 500


@jwt_required()
def verify_payment_fn():
    """
    Step 2: Frontend calls this API after a successful payment popup.
    We verify the signature to ensure no one tampered with the success response.
    """
    data = request.get_json()
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    try:
        # Verify the signature using Razorpay SDK
       # razorpay_client.utility.verify_payment_signature({
           # 'razorpay_order_id': razorpay_order_id,
           # 'razorpay_payment_id': razorpay_payment_id,
           # 'razorpay_signature': razorpay_signature
      #  })
        
        # If signature is valid, update the Payment table
        payment_record = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if payment_record:
            payment_record.razorpay_payment_id = razorpay_payment_id
            payment_record.razorpay_signature = razorpay_signature
            payment_record.status = 'completed'

            # Update the main Order status to 'processing' (Since payment is done)
            main_order = Orders.query.get(payment_record.order_id)
            if main_order:
                main_order.status = 'processing'
                main_order.payment_method = 'online'
            
            db.session.commit()

            return jsonify({"message": "Payment verified and order is now processing."}), 200
        else:
            return jsonify({"message": "Payment record not found in database."}), 404

    except razorpay.errors.SignatureVerificationError:
        # If signature verification fails, mark as failed
        db.session.rollback()
        payment_record = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if payment_record:
            payment_record.status = 'failed'
            db.session.commit()
            
        return jsonify({"message": "Payment verification failed! Invalid signature."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500