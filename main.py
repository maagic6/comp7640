# main.py

from fastapi import FastAPI
# --- Add imports ---
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# -----------------
from app.core.config import settings
# Import ONLY necessary routers now
from app.api.endpoints import vendors, products, transactions, health
# --- REMOVE frontend router import if it's empty ---
# from app.api.endpoints import frontend
# ---------------------------------------------------
from app.core.db_init import init_db
# from fastapi.middleware.cors import CORSMiddleware # Keep if needed

# --- Define Static Directory Path ---
# Calculate path relative to main.py (assuming main.py is in the root or similar)
# Adjust if main.py is elsewhere. If main.py is at the root:
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "app" / "views"
# ------------------------------------


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""...""",
    license_info={...}
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("Database initialization check complete.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {str(e)}")


# --- Include API routers ---
# These handle specific API paths like /products, /vendors, etc.
app.include_router(health.router)
app.include_router(vendors.router)
app.include_router(products.router)
app.include_router(transactions.router)


# --- Mount Static files LAST ---
# Mount static files AFTER API routers to avoid conflicts if an API route
# accidentally matches a static file path.
# Use html=True to automatically serve index.html for the root path '/'.
app.mount(
    "/",
    StaticFiles(directory=STATIC_DIR, html=True),
    name="static_frontend"
)
# -----------------------------


if __name__ == "__main__":
    import uvicorn
    # Uvicorn run command remains the same
    # Make sure you have 'python-multipart' installed: pip install python-multipart
    uvicorn.run(app, host="0.0.0.0", port=8000) # Removed reload for clarity, add back if needed