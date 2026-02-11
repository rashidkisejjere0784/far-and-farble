
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import imghdr
from typing import List
from PIL import Image as PILImage
from database import SessionLocal
from models.PetImage import PetImage as PetImageModel
from schemas.pet_image import PetImageResponseSchema, PetImageRequestSchema
from utils.encode import encrypt_int, decrypt_string
from openai import OpenAI
import base64
from utils.prompts import PROMPTS_DICT

client = OpenAI()

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploaded_images"
GENERATED_IMAGES_DIR = "generated_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
# Define accepted image types
ACCEPTED_IMAGE_TYPES = ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_image(file: UploadFile) -> bool:
    """Validate if the uploaded file is a valid image and meets requirements."""
    # Check content type
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        return False
    
    # Read the first chunk to detect file type
    contents = file.file.read(1024)
    file.file.seek(0)  # Reset file pointer
    
    # Use imghdr to detect the image type
    image_type = imghdr.what(None, contents)
    if not image_type or image_type not in ACCEPTED_IMAGE_TYPES:
        return False
    
    return True

@router.post("/upload-pet-image/", 
             response_model=PetImageResponseSchema, 
             status_code=status.HTTP_201_CREATED)
async def upload_pet_image(
    Image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate file size
    if Image.size and Image.size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds the maximum allowed size of {MAX_IMAGE_SIZE // (1024 * 1024)} MB"
        )

    # Check if it's actually an image
    if not validate_image(Image):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Uploaded file is not a valid image. Only {', '.join(ACCEPTED_IMAGE_TYPES)} formats are supported."
        )

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    try:
        # Read upload into Pillow
        Image.file.seek(0)
        pil_img = PILImage.open(Image.file)

        # Convert to RGBA if it has transparency, else to RGB
        if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
            pil_img = pil_img.convert("RGBA")
        else:
            pil_img = pil_img.convert("RGB")

        # Generate a unique PNG filename
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save as PNG
        pil_img.save(file_path, format="PNG")

        # Persist record in DB
        pet_image = PetImageModel(
            image_url=file_path,
            generated_images_folder_path=None
        )
        db.add(pet_image)
        db.commit()
        db.refresh(pet_image)

        return PetImageResponseSchema(
            image_url=file_path,
            encoded_image_id=encrypt_int(pet_image.id),
        )

    except Exception as e:
        # Cleanup on error
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )     
              
@router.post("/generate-image")
async def generate_image(
    details: PetImageRequestSchema,
    db: Session = Depends(get_db),
):
    try:
        # decrypt the image ID
        decrypted_id = decrypt_string(details.image_id)
        pet_image = db.query(PetImageModel).filter(PetImageModel.id == decrypted_id).first()
        
        if not pet_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Here you would call your image generation logic
        result = client.images.edit(
        model="gpt-image-1",
        image=[
                open("image_templates/magistrate_template.png", "rb"),
                open(pet_image.image_url, "rb")
            ],
            prompt=PROMPTS_DICT['magistrate_prompt_cat']
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # save the generated image to generated_images_folder_path
        generated_folder_path = os.path.join(GENERATED_IMAGES_DIR, str(uuid.uuid4()))
        os.makedirs(generated_folder_path, exist_ok=True)
        generated_image_path = os.path.join(generated_folder_path, "generated_image.png")

        with open(generated_image_path, "wb") as f:
            f.write(image_bytes)

        print(decrypted_id, pet_image.image_url)

        return {
                "message": "Image generated successfully",
                "generated_image_path": generated_image_path,
                "image_url": pet_image.image_url,
                "encoded_image_id": decrypted_id
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )
        
# Download the Images from the generated_images_folder_path only if the user has paid
@router.get("/download-image/{image_id}")
async def download_image(
    image_id: str,
    db: Session = Depends(get_db),
):
    try:
        # decrypt the image ID
        decrypted_id = decrypt_string(image_id)
        pet_image = db.query(PetImageModel).filter(PetImageModel.id == decrypted_id).first()

        if not pet_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        if not pet_image.is_payed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Image not paid for"
            )
            
        # zip the files in the generated_images_folder_path but check if generated_images_folder_path is not None
        if pet_image.generated_images_folder_path:
            folder_path = pet_image.generated_images_folder_path
            zip_filename = f"{uuid.uuid4()}.zip"
            zip_filepath = os.path.join(GENERATED_IMAGES_DIR, zip_filename)

            shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', folder_path)
            
            return {
                "message": "Image downloaded successfully",
                "download_link": zip_filepath
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated images folder not found"
            )


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image download failed: {str(e)}"
        )