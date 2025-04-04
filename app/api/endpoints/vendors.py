from fastapi import APIRouter, HTTPException, Query, Path
from app.models.schemas import VendorCreate, VendorResponse
from app.services.vendor_service import VendorService
from typing import List

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/",
    response_model=List[VendorResponse],
    summary="Get all vendors",
    description="Retrieve a list of all vendors registered on the platform",
    responses={
        200: {
            "description": "List of vendors retrieved successfully",
            "content": {
                "application/json": {
                    "example": [{
                        "vendor_id": 1,
                        "business_name": "Tech Store",
                        "customer_feedback_score": 4.5,
                        "geographical_presence": "New York",
                        "inventory": 100
                    }]
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def get_all_vendors():
    """
    Retrieve all vendors with their details:
    - Vendor ID
    - Business name
    - Customer feedback score
    - Geographical presence
    - Inventory count
    """
    try:
        vendors = await VendorService.get_all_vendors()
        return vendors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/",
    response_model=VendorResponse,
    status_code=201,
    summary="Create new vendor",
    description="Register a new vendor on the platform",
    responses={
        201: {
            "description": "Vendor created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "vendor_id": 1,
                        "business_name": "Tech Store",
                        "customer_feedback_score": 4.5,
                        "geographical_presence": "New York",
                        "inventory": 100
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def create_vendor(vendor: VendorCreate):
    """
    Create a new vendor with the following information:
    - **vendor_id**: Unique identifier for the vendor
    - **business_name**: Name of the vendor's business
    - **customer_feedback_score**: Optional rating score
    - **geographical_presence**: Location of operation
    - **inventory**: Current inventory count
    """
    try:
        result = await VendorService.create_vendor(vendor)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
