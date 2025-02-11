import os
import logging
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from bson import ObjectId
from app import mongo

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Adjust level as needed
logger = logging.getLogger(__name__)

upload_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload-avatar/<user_id>', methods=['POST'])
def upload_avatar(user_id):
    if 'file' not in request.files:
        logger.warning('No file part in request')
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        logger.warning('No selected file')
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        
        # Save the file
        try:
            file.save(filepath)
            logger.info(f'File saved successfully at {filepath}')
        except Exception as e:
            logger.error(f'Error saving file: {e}')
            return jsonify({'message': 'Error saving file'}), 500

        # Update user profile with avatar path
        try:
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'avatar': filename}}
            )
            logger.info(f'User {user_id} avatar updated to {filename}')
        except Exception as e:
            logger.error(f'Error updating avatar for user {user_id}: {e}')
            return jsonify({'message': 'Error updating avatar in database'}), 500

        return jsonify({'message': 'Avatar uploaded successfully', 'avatar': filename}), 200

    logger.warning(f'Invalid file type: {file.filename}')
    return jsonify({'message': 'Invalid file type'}), 400

@upload_bp.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)

    # Log the attempt to serve the file
    logger.info(f"Attempting to serve file: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f'File not found: {file_path}')
        return jsonify({'message': 'File not found'}), 404
    
    logger.info(f'Serving file: {file_path}')
    return send_from_directory(upload_folder, filename)
