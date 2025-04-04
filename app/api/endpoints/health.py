from fastapi import APIRouter, HTTPException
from app.core.database import db, DatabaseError
from typing import Dict

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
    responses={500: {"description": "Internal server error"}}
)

@router.get(
    "/",
    summary="Health check",
    description="Check if the API and database connection are working",
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Database connected successfully",
                        "pool_size": 6
                    }
                }
            }
        },
        500: {
            "description": "System unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Database connection failed: Connection refused"
                    }
                }
            }
        }
    }
)
async def health_check() -> Dict[str, str]:
    """
    Check system health and database connection

    Returns:
        - Connection status
        - Connection pool information
        - Detailed error message if connection fails
    """
    try:
        result = db.test_connection()
        return result
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
