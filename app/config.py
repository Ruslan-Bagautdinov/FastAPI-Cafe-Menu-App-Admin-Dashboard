import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

HOME_DB = os.getenv('HOME_DB', False)
HOME_EMAIL = os.getenv('HOME_EMAIL', False)

WORK_DATABASE_URL = os.getenv('WORK_DATABASE_URL')
LOCAL_DATABASE_URL = os.getenv('LOCAL_DATABASE_URL')

LOCAL_SMTP_SERVER = os.getenv('LOCAL_SMTP_SERVER')
LOCAL_SMTP_PORT = os.getenv('LOCAL_SMTP_PORT')
LOCAL_SENDER_EMAIL = os.getenv('LOCAL_SENDER_EMAIL')
LOCAL_SENDER_PASSWORD = os.getenv('LOCAL_SENDER_PASSWORD')

WORK_SMTP_SERVER = os.getenv('WORK_SMTP_SERVER')
WORK_SMTP_PORT = os.getenv('WORK_SMTP_PORT')
WORK_SENDER_EMAIL = os.getenv('WORK_SENDER_EMAIL')
WORK_SENDER_PASSWORD = os.getenv('WORK_SENDER_PASSWORD')

LOCAL_SERVER_HOST = os.getenv('LOCAL_SERVER_HOST')
LOCAL_SERVER_PORT = os.getenv('LOCAL_SERVER_PORT')
WORK_SERVER_HOST = os.getenv('WORK_SERVER_HOST')
WORK_SERVER_PORT = os.getenv('WORK_SERVER_PORT')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PHOTO_FOLDER = os.path.join(BASE_DIR, 'img')

MIME_TYPES = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "webp": "image/webp",
}
