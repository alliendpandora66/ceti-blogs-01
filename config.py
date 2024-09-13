import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Máximo 100 MB por archivo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
