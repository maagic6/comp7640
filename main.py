from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.api.endpoints import vendors, products, transactions, health
from app.core.db_init import init_db

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "app" / "views"


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    E-commerce Platform API with vendor, product, and transaction management.
    Provides endpoints for:
    - Vendor onboarding and listing.
    - Product browsing, searching, and creation.
    - Transaction creation.
    - Health checks.
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
        print("Database initialization check complete.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {str(e)}")


# api routers
app.include_router(health.router)
app.include_router(vendors.router)
app.include_router(products.router)
app.include_router(transactions.router)

# mount
app.mount(
    "/",
    StaticFiles(directory=STATIC_DIR, html=True),
    name="static_frontend"
)
# -----------------------------


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)