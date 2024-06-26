from os import getenv, path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = getenv('SECRET_KEY', 'secret-key')
ALGORITHM = getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))


WORK_DATABASE_URL = getenv('WORK_DATABASE_URL')
LOCAL_DATABASE_URL = getenv('LOCAL_DATABASE_URL')

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
