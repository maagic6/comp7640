from fastapi import APIRouter, HTTPException, Query, Path
from app.models.schemas import ProductCreate, ProductResponse
from app.services.product_service import ProductService
from typing import List

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/vendor/{vendor_id}",
    response_model=List[ProductResponse],
    summary="Get vendor products",
    description="Retrieve all products for a specific vendor",
    responses={
        200: {
            "description": "List of products retrieved successfully",
            "content": {
                "application/json": {
                    "example": [{
                        "product_id": 1,
                        "product_name": "Laptop",
                        "price": 999.99,
                        "products_nature": "Electronics"
                    }]
                }
            }
        },
        404: {"description": "Vendor not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_vendor_products(
    vendor_id: int = Path(..., title="Vendor ID", description="Unique identifier of the vendor")
):
    """
    Retrieve all products for a specific vendor:
    - List of products with their details
    - Includes price and nature of products
    """
    try:
        products = await ProductService.get_vendor_products(vendor_id)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201,
    summary="Create new product",
    description="Add a new product to vendor's catalog",
    responses={
        201: {
            "description": "Product created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "product_id": 1,
                        "product_name": "Laptop",
                        "price": 999.99,
                        "products_nature": "Electronics"
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def create_product(product: ProductCreate):
    """
    Create a new product with the following information:
    - **product_id**: Unique identifier for the product
    - **product_name**: Name of the product
    - **price**: Product price (must be greater than 0)
    - **products_nature**: Category or nature of the product
    - **vendor_id**: ID of the vendor selling this product
    """
    try:
        result = await ProductService.create_product(product)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/search",
    response_model=List[ProductResponse],
    summary="Search products",
    description="Search products by name or nature/tags",
    responses={
        200: {
            "description": "Search results retrieved successfully",
            "content": {
                "application/json": {
                    "example": [{
                        "product_id": 1,
                        "product_name": "Laptop",
                        "price": 999.99,
                        "products_nature": "Electronics"
                    }]
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def search_products(
    q: str = Query(..., title="Search Query", description="Search term for product name or nature")
):
    """
    Search for products using:
    - Product name
    - Product nature/tags
    Returns matching products with their details
    """
    try:
        products = await ProductService.search_products(q)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
