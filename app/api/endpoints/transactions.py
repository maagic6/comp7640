from fastapi import APIRouter, HTTPException, Body, status
from app.models.schemas import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from app.core.database import DatabaseError
from typing import List

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
    description="Create a new transaction for product purchase with validation",
    responses={
        201: {
            "description": "Transaction created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "transaction_id": 1,
                        "message": "Transaction created successfully",
                        "vendors": [1, 2]
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with ID 123 does not exist"
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def create_transaction(
    transaction: TransactionCreate = Body(
        ...,
        example={
            "customer_id": 1,
            "products": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ]
        }
    )
):
    """
    Create a new transaction with validation:
    - Verifies customer exists
    - Verifies all products exist
    - Links transaction to vendors
    - Records product quantities

    Parameters:
    - **customer_id**: ID of the customer making the purchase
    - **products**: List of products being purchased
        - product_id: ID of the product
        - quantity: Number of items (default: 1)
    """
    try:
        result = await TransactionService.create_transaction(transaction)
        return result
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
