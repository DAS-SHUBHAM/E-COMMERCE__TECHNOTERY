from flask import request
from flask_socketio import emit
from extensions import socketio, db
from Models.chat_model import ChatMessage
from flask_jwt_extended import decode_token

# Dictionary to store active user mappings dynamically
ONLINE_USERS = {}

@socketio.on('connect')
def handle_connect():
    """
    Handles incoming WebSocket connections, decodes the JWT token,
    and maps the unique active Session ID (SID) to the user's role.
    """
    token = request.args.get('token')
    if not token:
        return False
    
    try:
        decoded_token = decode_token(token)
        role = int(decoded_token.get('role', 0))
        user_id = int(decoded_token.get('sub'))
        
        # Map the current socket connection hardware address (SID) to the role
        if role == 1:
            ONLINE_USERS['admin'] = request.sid
            ONLINE_USERS['admin_id'] = user_id
            print(f"DEBUG: Admin (ID: {user_id}) connected on SID: {request.sid}")
        elif role == 2:
            ONLINE_USERS['seller'] = request.sid
            ONLINE_USERS['seller_id'] = user_id
            print(f"DEBUG: Seller (ID: {user_id}) connected on SID: {request.sid}")
            
        emit('server_message', {'msg': 'Connected to secure chat server with database tracking'}, room=request.sid)
    except Exception as e:
        print(f"DEBUG: Connection error: {str(e)}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """
    Cleans up active session mappings when a user disconnects.
    """
    for key in list(ONLINE_USERS.keys()):
        if ONLINE_USERS[key] == request.sid:
            print(f"DEBUG: Session disconnected for connection endpoint.")
            # Clear mappings safely
            if key == 'admin':
                ONLINE_USERS.pop('admin', None)
                ONLINE_USERS.pop('admin_id', None)
            elif key == 'seller':
                ONLINE_USERS.pop('seller', None)
                ONLINE_USERS.pop('seller_id', None)
            break

@socketio.on('send_message')
def handle_message(data):
    """
    Persists the message payload into MySQL first, then routes it 
    directly to the recipient's live socket session.
    """
    try:
        msg_text = data['message']
        role = int(data['role'])  # 1 for Admin, 2 for Seller

        # Determine sender and receiver IDs dynamically for the Database
        if role == 1:
            # Admin is sending to Seller
            sender_id = ONLINE_USERS.get('admin_id', 1)
            receiver_id = ONLINE_USERS.get('seller_id', 5)  # Fallback to 5 if not mapped
        else:
            # Seller is sending to Admin
            sender_id = ONLINE_USERS.get('seller_id', 5)
            receiver_id = ONLINE_USERS.get('admin_id', 1)   # Fallback to 1 if not mapped

        # 1. CRITICAL: Persist data into MySQL database table
        new_msg = ChatMessage(sender_id=sender_id, receiver_id=receiver_id, message=msg_text)
        db.session.add(new_msg)
        db.session.commit()
        print(f"DEBUG: Message successfully saved in MySQL. ID: {new_msg.id}")

        # Construct payload with DB timestamp
        payload = {
            'id': new_msg.id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message': msg_text,
            'timestamp': str(new_msg.created_at),
            'sender_role': role
        }

        # 2. Return live acknowledgment copy back to the sender
        emit('receive_message', payload, room=request.sid)

        # 3. Deliver live message to the opposite party via dynamic Session ID mapping
        if role == 1:
            if 'seller' in ONLINE_USERS:
                emit('receive_message', payload, room=ONLINE_USERS['seller'])
                print("DEBUG: Message delivered live to Seller's active session.")
            else:
                print("DEBUG: Seller is currently offline. Message cached in MySQL.")
        else:
            if 'admin' in ONLINE_USERS:
                emit('receive_message', payload, room=ONLINE_USERS['admin'])
                print("DEBUG: Message delivered live to Admin's active session.")
            else:
                print("DEBUG: Admin is currently offline. Message cached in MySQL.")

    except Exception as e:
        db.session.rollback()  # Rollback database transaction on failure
        print(f"DEBUG: Critical Error in send_message: {str(e)}")