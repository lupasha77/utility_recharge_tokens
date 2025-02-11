# backend/app/routes/messages.py 
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
from app import mongo 
import json

messages_bp = Blueprint('messages', __name__)
 
def get_user(email):
    return mongo.db.users.find_one({'email': email})
def get_registered_users():
    return [user['email'] for user in mongo.db.users.find({}, {'email': 1})]
# Initialize encryption key


class MessageEncryption:
    def __init__(self):
        # Generate or load encryption keys
        self.salt = self._get_or_generate_salt()
        self.master_key = self._get_or_generate_master_key()
        self.cipher_suite = self._initialize_cipher()

    def _get_or_generate_salt(self):
        """Get existing salt from env or generate new one"""
        stored_salt = os.environ.get('ENCRYPTION_SALT')
        if stored_salt:
            return base64.b64decode(stored_salt)
        return os.urandom(16)

    def _get_or_generate_master_key(self):
        """Get existing master key from env or generate new one"""
        stored_key = os.environ.get('MASTER_KEY')
        if stored_key:
            return stored_key
        return base64.b64encode(os.urandom(32)).decode('utf-8')

    def _initialize_cipher(self):
        """Initialize the Fernet cipher with derived key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)

    def encrypt_message(self, message: str) -> str:
        """Encrypt a message"""
        return self.cipher_suite.encrypt(message.encode()).decode()

    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt a message"""
        return self.cipher_suite.decrypt(encrypted_message.encode()).decode()

    def generate_new_keys(self):
        """Generate new salt and master key - use this to create your initial keys"""
        new_salt = base64.b64encode(os.urandom(16)).decode('utf-8')
        new_master_key = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        print("\nGenerated new encryption keys:")
        print(f"ENCRYPTION_SALT={new_salt}")
        print(f"MASTER_KEY={new_master_key}")
        
        return new_salt, new_master_key

# Usage in your Flask routes
encryption = MessageEncryption()


class MessageStatus:
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'

@messages_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    try:
        data = request.get_json()
        sender = get_jwt_identity()
        recipient = data.get('recipient')
        content = data.get('content')
        
        if not recipient or not content:
            return jsonify({'message': 'Recipient and content are required'}), 400
        
        recipient_user = get_user(recipient)
        if not recipient_user:
            return jsonify({'message': 'Recipient not found'}), 404
        
        # Encrypt the message content
        encrypted_content = encryption.encrypt_message(content)
        
        message = {
            'sender': sender,
            'recipient': recipient,
            'content': encrypted_content,
            'timestamp': datetime.utcnow(),
            'read': False,
            'status': MessageStatus.SENT,  # Set initial status as SENT
            'delivery_timestamp': datetime.utcnow()  # Track when message was delivered
        }
        
        result = mongo.db.messages.insert_one(message)
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500



# Modify the get_messages route to handle encryption
@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    try:
        current_user = get_jwt_identity()
        folder = request.args.get('folder', 'all')
        
        # Base query for messages
        query = {
            '$or': [
                {'recipient': current_user},
                {'sender': current_user}
            ]
        }
        
        # Add folder-specific filters
        if folder != 'all':
            if folder == 'inbox':
                query = {'recipient': current_user}
            elif folder == 'outbox':
                query = {'sender': current_user, 'status': 'pending'}
            elif folder == 'sent':
                query = {'sender': current_user, 'status': 'sent'}

        messages = list(mongo.db.messages.find(query).sort('timestamp', -1))

        # Process messages
        processed_messages = []
        for message in messages:
            try:
                # Convert ObjectId to string
                message['_id'] = str(message['_id'])
                if 'parent_id' in message:
                    message['parent_id'] = str(message['parent_id'])
                
                # Convert datetime to ISO format string
                message['timestamp'] = message['timestamp'].isoformat()
                
                # Decrypt content
                try:
                    decrypted_content = encryption.decrypt_message(message['content'])
                    message['content'] = json.dumps({
                        'decryptedContent': decrypted_content,
                        'isDecrypted': True
                    })
                except Exception as e:
                    print(f"Decryption error for message {message['_id']}: {str(e)}")
                    message['content'] = json.dumps({
                        'decryptedContent': '[Message decryption failed]',
                        'isDecrypted': False
                    })
                
                processed_messages.append(message)
                
            except Exception as e:
                print(f"Error processing message {message.get('_id', 'unknown')}: {str(e)}")
                continue

        return jsonify(processed_messages), 200

    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500

@messages_bp.route('/messages/counts', methods=['GET'])
@jwt_required()
def get_message_counts():
    try:
        current_user = get_jwt_identity()
        
        # Get counts for each folder
        inbox_count = mongo.db.messages.count_documents({
            'recipient': current_user,
            'status': 'sent',
            'read': False  # Changed from isRead to read to match schema
        })
        
        outbox_count = mongo.db.messages.count_documents({
            'sender': current_user,
            'status': 'pending'
        })
        
        sent_count = mongo.db.messages.count_documents({
            'sender': current_user,
            'status': 'sent'
        })
        
        return jsonify({
            'inbox': inbox_count,
            'outbox': outbox_count,
            'sent': sent_count
        }), 200
        
    except Exception as e:
        print(f"Error getting message counts: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500
@messages_bp.route('/messages/<message_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_message(message_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        content = data.get('content')
        
        # Get original message
        original_message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
        if not original_message:
            return jsonify({'message': 'Original message not found'}), 404
            
        # Create reply message
        reply = {
            'sender': current_user,
            'recipient': original_message['sender'],
            'content': content,
            'timestamp': datetime.utcnow(),
            'parent_id': ObjectId(message_id),
            'isRead': False,
            'status': 'sent'
        }
        
        result = mongo.db.messages.insert_one(reply)
        return jsonify({
            'message': 'Reply sent successfully',
            'message_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error sending reply: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500


from flask import jsonify
from bson import ObjectId
from datetime import datetime

@messages_bp.route('/<message_id>/read', methods=['PATCH','OPTIONS'])
@jwt_required()
def mark_message_read(message_id):
     # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response
    try:
        current_user = get_jwt_identity()
        
        # Validate message exists and user has permission
        message = mongo.db.messages.find_one({
            '_id': ObjectId(message_id),
            '$or': [
                {'recipient': current_user},
                {'sender': current_user}
            ]
        })
        
        if not message:
            return jsonify({
                'message': 'Message not found or you don\'t have permission'
            }), 404
            
        # Update message read status
        result = mongo.db.messages.update_one(
            {'_id': ObjectId(message_id)},
            {
                '$set': {
                    'read': True,
                    'read_timestamp': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({
                'message': 'Message marked as read',
                'message_id': message_id
            }), 200
        else:
            return jsonify({
                'message': 'Message status was not updated'
            }), 400
            
    except Exception as e:
        print(f"Error marking message as read: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500

@messages_bp.route('/messages/<message_id>/unread', methods=['PATCH'])
@jwt_required()
def mark_message_unread(message_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response
    try:
        current_user = get_jwt_identity()
        
        # Validate message exists and user has permission
        message = mongo.db.messages.find_one({
            '_id': ObjectId(message_id),
            '$or': [
                {'recipient': current_user},
                {'sender': current_user}
            ]
        })
        
        if not message:
            return jsonify({
                'message': 'Message not found or you don\'t have permission'
            }), 404
            
        # Check if message is in valid folders for unread status
        valid_folders = ['inbox', 'sent', 'outbox']
        message_folder = message.get('folder', 'inbox')  # Default to inbox if folder not specified
        
        if message_folder not in valid_folders:
            return jsonify({
                'message': f'Cannot mark messages as unread in {message_folder} folder'
            }), 400
            
        # Update message read status
        result = mongo.db.messages.update_one(
            {'_id': ObjectId(message_id)},
            {
                '$set': {
                    'read': False,
                    'unread_timestamp': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({
                'message': 'Message marked as unread',
                'message_id': message_id
            }), 200
        else:
            return jsonify({
                'message': 'Message status was not updated'
            }), 400
            
    except Exception as e:
        print(f"Error marking message as unread: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500
    
# Add a cleanup task for pending messages
def cleanup_pending_messages():
    """Delete pending messages older than 24 hours"""
    cleanup_time = datetime.utcnow() - timedelta(hours=24)
    mongo.db.messages.delete_many({
        'status': MessageStatus.PENDING,
        'timestamp': {'$lt': cleanup_time}
    })

def get_messages():
    try:
        user = get_jwt_identity()
        folder = request.args.get('folder', 'inbox')
        
        if folder == 'inbox':
            query = {'recipient': user}
        elif folder == 'outbox':
            query = {'sender': user}
        else:
            query = {'$or': [{'sender': user}, {'recipient': user}]}
        
        messages = list(mongo.db.messages.find(query).sort('timestamp', -1))
        
        # Decrypt messages
        for message in messages:
            message['_id'] = str(message['_id'])
            message['timestamp'] = message['timestamp'].isoformat()
            try:
                message['content'] = encryption.decrypt_message(message['content'])
            except Exception as e:
                print(f"Error decrypting message {message['_id']}: {str(e)}")
                message['content'] = '[Message decryption failed]'
        
        return jsonify(messages), 200
        
    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500
@messages_bp.route('/messages/<message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    try:
        user = get_jwt_identity()
        
        message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
        if not message:
            return jsonify({'message': 'Message not found'}), 404
            
        update_field = None
        if message['sender'] == user:
            update_field = 'deleted_by_sender'
        elif message['recipient'] == user:
            update_field = 'deleted_by_recipient'
            
        if update_field:
            mongo.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {update_field: True}}
            )
            
            # If both sender and recipient have deleted, actually remove the message
            message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
            if message.get('deleted_by_sender') and message.get('deleted_by_recipient'):
                mongo.db.messages.delete_one({'_id': ObjectId(message_id)})
            
        return jsonify({'message': 'Message deleted successfully'}), 200
        
    except Exception as e:
        mongo.db.error_logs.insert_one({
            'error': str(e),
            'timestamp': datetime.utcnow(),
            'endpoint': f'/messages/{message_id}',
            'method': 'DELETE'
        })
        return jsonify({'message': 'An error occurred'}), 500
@messages_bp.route('/messages/<message_id>', methods=['PUT'])
@jwt_required()
def update_message(message_id):
    user = get_jwt_identity()
    data = request.get_json()
    
    message = mongo.db.messages.find_one({
        '_id': ObjectId(message_id),
        'recipient': user
    })
    
    if not message:
        return jsonify({'message': 'Message not found'}), 404
    
    # Update read status
    if 'read' in data:
        mongo.db.messages.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'read': data['read']}}
        )
    
    return jsonify({'message': 'Message updated successfully'}), 200


@messages_bp.route('/users', methods=['GET'])
@jwt_required()
def get_registered_contacts():
    current_user = get_jwt_identity()
    users = get_registered_users()
    # Remove current user from the list
    users = [user for user in users if user != current_user]
    return jsonify(users), 200