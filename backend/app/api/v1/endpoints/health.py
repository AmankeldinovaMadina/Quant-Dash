from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthResponse(
        status="healthy",
        message="Quant-Dash Backend API is running",
        version="1.0.0"
    )
