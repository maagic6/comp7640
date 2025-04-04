from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME: str = "E-commerce Platform API"
    APP_VERSION: str = "1.0.0"
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_NAME: str = os.getenv('DB_NAME', 'project_db')

settings = Settings()
