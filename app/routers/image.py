from fastapi import APIRouter, Query, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
import os
import io

from app.utils.functions import read_photo, save_upload_file
from app.config import MIME_TYPES
from app.config import MAIN_PHOTO_FOLDER

router = APIRouter()

default_avatar_path = os.path.join(MAIN_PHOTO_FOLDER, 'default_cafe_04.jpeg')


@router.get("/")
async def get_image(
    restaurant_id: int = Query(None, description="The ID of the restaurant"),
    photo: str = Query(None, description="The filename of the photo")
):
    """
    Retrieves a photo from the static photo folder or returns a default photo if the specified photo is not found.

    Args:
        restaurant_id (int): The ID of the restaurant.
        photo (str): The filename of the photo to retrieve. If not provided, the default photo will be returned.

    Returns:
        StreamingResponse: A streaming response containing the photo bytes.

    Raises:
        HTTPException: 404 error if the default photo is not found.
    """
    if restaurant_id and photo:
        restaurant_id = str(restaurant_id)
        full_path = os.path.join(MAIN_PHOTO_FOLDER, restaurant_id, photo)
    else:
        full_path = default_avatar_path

    if os.path.exists(full_path):
        print('path exists', full_path)
        photo_bytes = await read_photo(full_path)
    else:
        print('path NOT exists', full_path)
        photo_bytes = None

    if photo_bytes is None:
        print('Loading default photo due to previous error or non-existence')
        photo_bytes = await read_photo(default_avatar_path)

    if photo_bytes is None:
        raise HTTPException(status_code=404, detail="Default photo not found")

    # Determine the media type based on the file extension
    _, default_extension = os.path.splitext(default_avatar_path)
    default_extension = default_extension[1:].lower()  # Remove the leading dot and convert to lowercase

    if photo:
        _, file_extension = os.path.splitext(photo)
        file_extension = file_extension[1:].lower() if file_extension else default_extension
    else:
        file_extension = default_extension

    print('photo', photo, 'file_extension', file_extension)

    media_type = MIME_TYPES.get(file_extension, "application/octet-stream")

    return StreamingResponse(io.BytesIO(photo_bytes), media_type=media_type)


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), restaurant_id: str = None, filename: str = None):

    ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "gif", "bmp", "webp"}

    if not restaurant_id:
        raise HTTPException(status_code=400, detail="Restaurant ID is required.")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # Check if the file extension is in the allowed list
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' is not allowed. Allowed types are {', '.join(ALLOWED_EXTENSIONS)}.")

    destination = os.path.join(MAIN_PHOTO_FOLDER, restaurant_id, filename)

    os.makedirs(os.path.dirname(destination), exist_ok=True)

    await save_upload_file(file, destination)
    return {"filename": filename, "destination": destination}
