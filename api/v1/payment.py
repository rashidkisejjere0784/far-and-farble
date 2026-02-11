from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from utils.auth import send_verification_email, generate_verification_token
from models.PetImage import PetImage as PetImageModel
from schemas.payment import PaymentIntentImageSchema, PaymentResponseSchema, PaymentInputSchema, PaymentConfirmationSchema
from utils.encode import decrypt_string
from database import SessionLocal
import os
from dotenv import load_dotenv
import stripe

router = APIRouter()
load_dotenv()

stripe.api_key = os.getenv("STRIPE_PRIVATE_KEY")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create-payment-intent/", response_model=PaymentIntentImageSchema)
def create_payment_intent(payment: PaymentInputSchema, db: Session = Depends(get_db)):

    try:
        intent = stripe.PaymentIntent.create(
            amount=1900,                 # cents
            currency="usd",
            payment_method_types=["card"]
        )
        # get the pet image where id is image_id, then update the stripe_payment_id
        pet_image = db.query(PetImageModel).filter_by(id=decrypt_string(payment.image_id)).first()

        if not pet_image:
            raise HTTPException(status_code=404, detail="Pet image not found")

        pet_image.stripe_payment_id = intent.id
        db.commit()

        return PaymentIntentImageSchema(
            image_id=payment.image_id,
            stripe_payment_id=intent.id,
            client_secret=intent.client_secret
        )
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error creating payment intent")

@router.post("/confirm-payment/", response_model=PaymentResponseSchema)
def confirm_payment(req: PaymentConfirmationSchema, db: Session = Depends(get_db)):
    # 1) Retrieve the PaymentIntent from Stripe to verify status
    try:
        intent = stripe.PaymentIntent.retrieve(req.stripe_payment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid payment_intent_id")

    # 2) Look up our Order
    order = db.query(PetImageModel).filter_by(stripe_payment_id=intent.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 3) Check status
    if intent.status == "succeeded" and not order.is_payed:
        order.is_payed = True
        db.commit()
        
        return PaymentResponseSchema(
            image_id=req.image_id,
            payment_status=intent.status,
            message="Payment was successful."
        )

    if intent.status != "succeeded":
        return PaymentResponseSchema(
            image_id=req.image_id,
            payment_status=intent.status,
            message="Payment was not successful."
        )

    # Already paid
    return PaymentResponseSchema(
        image_id=req.image_id,
        payment_status=intent.status,
        message="Payment was already completed."
    )