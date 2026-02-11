from pydantic import BaseModel

class PetImageResponseSchema(BaseModel):
    """
    Schema for pet image response.
    """
    image_url: str
    encoded_image_id: str
    
    
class PetImageRequestSchema(BaseModel):
    """
    Schema for pet image request.
    """
    image_id: str