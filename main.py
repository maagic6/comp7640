from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import vendors, products, transactions, health
from app.core.db_init import init_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    E-commerce Platform API that provides:
    * Vendor management
    * Product catalog management
    * Transaction processing
    * Health monitoring

    ## Vendors
    You can:
    * List all vendors
    * Create new vendors

    ## Products
    You can:
    * Browse vendor products
    * Add new products
    * Search products by name/tags

    ## Transactions
    You can:
    * Create purchase transactions

    ## Health
    You can:
    * Check API and database health
    * Monitor connection pool status
    """,
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {str(e)}")

# Include routers
app.include_router(health.router)
app.include_router(vendors.router)
app.include_router(products.router)
app.include_router(transactions.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
