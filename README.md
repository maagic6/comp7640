# E-commerce Platform API

A FastAPI-based e-commerce platform API with MySQL database.

## Prerequisites

- Python 3.8+
- MySQL server (Local MariaDB was used for testing)
- Git

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/maagic6/comp7640.git
cd comp7640
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

### 5. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Default customer with ID 1 will be added during initialization.

### 6. Access the API

Access the API through the frontend at `http://localhost:8000`.

### 7. Project Structure

- `app/`: Contains the FastAPI application and its components.
- `app/core/`: Core components for database operations and configuration.
- `app/models/`: Data models and schemas.
- `app/services/`: Business logic and services.
- `app/api/`: API endpoints and routes.
- `app/tests/`: Test cases for unit testing.
- `app/views/`: Frontend HTML and JavaScript.
- `app/main.py`: Entry point for the FastAPI application.
