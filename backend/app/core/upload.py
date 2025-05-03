import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, File, HTTPException

# Directory for file uploads
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Create if it doesn't exist


ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx"}  # Allowed file formats
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def upload_file(file: UploadFile = File(...)) -> str:
    """Uploads a file and returns its URL"""

    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file format (allowed: pdf, docx, pptx)")

    # Validate file size
    file.file.seek(0, 2)  # Move to the end of the file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to the beginning
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Generate a unique file name
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save the file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return the file URL as a string
    return f"/static/uploads/{unique_filename}"
