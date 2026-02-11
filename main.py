from fastapi import FastAPI, Request
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import uvicorn

from api.v1 import user
from api.v1 import model
from api.v1 import payment
from database import create_db_and_tables


# Create the database and tables
create_db_and_tables()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for user endpoints
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])

# Include routers for model endpoints
app.include_router(model.router, prefix="/api/v1/models", tags=["models"])

# Include routers for payment endpoints
app.include_router(payment.router, prefix="/api/v1/payments", tags=["payments"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Fur and Furble API"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(exc)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)