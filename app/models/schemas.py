from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class VendorBase(BaseModel):
    business_name: str = Field(..., description="Name of the business")
    customer_feedback_score: Optional[int] = Field(None, description="Customer feedback score")
    geographical_presence: str = Field(..., description="Geographical presence")
    inventory: str = Field(..., description="Inventory details")

class VendorCreate(BaseModel):
    vendor_id: int = Field(..., description="Unique vendor ID")
    business_name: str = Field(..., description="Name of the business")
    customer_feedback_score: Optional[float] = Field(None, description="Customer feedback score")
    geographical_presence: str = Field(..., description="Geographical presence")
    inventory: int = Field(..., description="Inventory count")

class VendorResponse(BaseModel):
    vendor_id: int
    business_name: str
    customer_feedback_score: Optional[float] = None
    geographical_presence: str
    inventory: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    price: float = Field(..., gt=0, description="Product price")
    products_nature: str = Field(..., description="Nature/category of the product")

class ProductCreate(BaseModel):
    product_id: int = Field(..., description="Unique product ID")
    product_name: str = Field(..., description="Name of the product")
    price: float = Field(..., gt=0, description="Product price")
    products_nature: str = Field(..., description="Nature/category of the product")
    vendor_id: int = Field(..., description="ID of the vendor")

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    products_nature: str

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    customer_id: int
    products: List[dict] = Field(..., description="List of products with quantities")

class TransactionResponse(BaseModel):
    transaction_id: int
    message: str

# Response types can be simple dictionaries, no need for special classes
VendorResponse = dict
ProductResponse = dict
