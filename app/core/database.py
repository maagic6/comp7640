import pymysql
from pymysql.err import OperationalError, InterfaceError
from dbutils.pooled_db import PooledDB
from app.core.config import settings
from typing import Dict, Any, List, Union

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class Database:
    def __init__(self):
        try:
            self.pool = PooledDB(
                creator=pymysql,
                mincached=2,
                maxcached=4,
                maxshared=3,
                blocking=True,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database pool: {str(e)}")

    def get_connection(self):
        try:
            return self.pool.connection()
        except (OperationalError, InterfaceError) as e:
            raise DatabaseError(f"Database connection failed: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Unexpected database error: {str(e)}")

    def execute_query(self, query: str, params: tuple = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Execute a query and return the result.
        Returns List[Dict] for SELECT, Dict for others.
        """
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    # strip whitespace
                    if query.strip().lower().startswith('select'):
                        return cursor.fetchall()
                    else:
                        connection.commit()
                        return {"affected_rows": cursor.rowcount}
        except Exception as e:
            raise DatabaseError(f"Query execution failed: {str(e)}")

    def test_connection(self) -> Dict[str, str]:
        """Test database connection"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return {
                        "status": "success",
                        "message": "Database connected successfully",
                    }
        except DatabaseError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"Database connection test failed: {str(e)}")

db = Database()
