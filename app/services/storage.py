import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def save_file(file, order_id):
    """
    Saves an uploaded file to the uploads directory.
    d:/.../app/uploads/order_{id}/{uuid}_{filename}
    Returns relative path from app root for DB storage.
    """
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    
    # Create order specific folder
    upload_folder = current_app.config['UPLOAD_FOLDER']
    order_folder = os.path.join(upload_folder, f'order_{order_id}')
    
    if not os.path.exists(order_folder):
        os.makedirs(order_folder)
        
    # Generate unique filename to prevent overwrites
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = os.path.join(order_folder, unique_name)
    
    file.save(file_path)
    
    # Return path relative to upload_folder for portability if needed, 
    # but prompt requested absolute path or just file path. 
    # Storing path relative to 'app/' or just the filename?
    # Let's store relative path from app root so we can serve/find it later easily.
    # relative: uploads/order_123/abc_file.stl
    
    rel_path = os.path.join('uploads', f'order_{order_id}', unique_name)
    # normalize separators
    rel_path = rel_path.replace('\\', '/')
    
    return rel_path
