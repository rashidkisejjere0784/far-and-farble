from pydantic import BaseModel


class PaymentIntentImageSchema(BaseModel):
    """
    Schema for creating a payment intent for an image.
    """
    image_id: str
    stripe_payment_id: str
    client_secret: str
    
class PaymentInputSchema(BaseModel):
    """
    Schema for input data to create a payment intent.
    """
    image_id: str
    
class PaymentResponseSchema(PaymentInputSchema):
    """
    Schema for the response of a payment intent creation.
    """
    payment_status: str
    message: str
    

class PaymentConfirmationSchema(BaseModel):
    """
    Schema for confirming a payment.
    """
    image_id: str
    stripe_payment_id: str