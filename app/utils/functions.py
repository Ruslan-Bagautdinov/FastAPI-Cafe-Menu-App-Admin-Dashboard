import aiofiles
import os

async def read_photo(photo_path):
    """
    Asynchronously reads the contents of a photo file.

    Args:
        photo_path (str): The path to the photo file.

    Returns:
        bytes | None: The binary data of the photo file if found and has a valid extension, otherwise None.

    Raises:
        FileNotFoundError: If the file at `photo_path` does not exist.
        Exception: For any other errors encountered while reading the file.
    """
    # Define the allowed file extensions and their corresponding MIME types
    allowed_extensions = {
        "jpeg",
        "jpg",
        "png",
        "gif",
        "bmp",
        "webp"
    }

    # Get the file extension
    _, file_extension = os.path.splitext(photo_path)
    file_extension = file_extension[1:].lower()  # Remove the leading dot and convert to lowercase

    print(f"File extension: {file_extension}")

    # Check if the file extension is allowed
    if file_extension not in allowed_extensions:
        print(f"Invalid file extension: {file_extension}")
        return None

    try:
        async with aiofiles.open(photo_path, 'rb') as photo_file:
            photo_data = await photo_file.read()
            return photo_data
    except FileNotFoundError:
        print(f"File not found: {photo_path}")
        return None
    except Exception as e:
        print(f"Error reading photo {photo_path}: {e}")
        return None
