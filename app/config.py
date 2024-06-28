from os import getenv, path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = getenv('SECRET_KEY', 'secret-key')
ALGORITHM = getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))

SMTP_SERVER = getenv('SMTP_SERVER')
SMTP_PORT = getenv('SMTP_PORT')
SENDER_EMAIL = getenv('SENDER_EMAIL')
SENDER_PASSWORD = getenv('SENDER_PASSWORD')

HOME_DB = getenv('HOME_DB', False)
HOME_EMAIL = getenv('HOME_EMAIL', False)

WORK_DATABASE_URL = getenv('WORK_DATABASE_URL')
LOCAL_DATABASE_URL = getenv('LOCAL_DATABASE_URL')

LOCAL_SMTP_SERVER = getenv('LOCAL_SMTP_SERVER')
LOCAL_SMTP_PORT = getenv('LOCAL_SMTP_PORT')
LOCAL_SENDER_EMAIL = getenv('LOCAL_SENDER_EMAIL')
LOCAL_SENDER_PASSWORD = getenv('LOCAL_SENDER_PASSWORD')

WORK_SMTP_SERVER = getenv('WORK_SMTP_SERVER')
WORK_SMTP_PORT = getenv('WORK_SMTP_PORT')
WORK_SENDER_EMAIL = getenv('WORK_SENDER_EMAIL')
WORK_SENDER_PASSWORD = getenv('WORK_SENDER_PASSWORD')


LOCAL_SERVER_HOST = getenv('LOCAL_SERVER_HOST')
LOCAL_SERVER_PORT = getenv('LOCAL_SERVER_PORT')
WORK_SERVER_HOST = getenv('WORK_SERVER_HOST')
WORK_SERVER_PORT = getenv('WORK_SERVER_PORT')


BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
RESTAURANTS_PHOTO_DIR = path.join(BASE_DIR, 'photo', 'restaurants')
DISHES_PHOTO_DIR = path.join(BASE_DIR, 'photo', 'dishes')

MIME_TYPES = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "webp": "image/webp",
}
