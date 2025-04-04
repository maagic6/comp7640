from app.core.database import db
from app.models.schemas import ProductCreate

class ProductService:
    @staticmethod
    async def get_vendor_products(vendor_id: int):
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                sql = """SELECT p.* FROM Products p
                        JOIN Vendor_Sells_Product vsp ON p.product_id = vsp.product_id
                        WHERE vsp.vendor_id = %s"""
                cursor.execute(sql, (vendor_id,))
                return cursor.fetchall()
        except Exception as e:
            raise e

    @staticmethod
    async def create_product(product: ProductCreate):
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                sql = """INSERT INTO Products
                        (product_id, product_name, price, products_nature)
                        VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (
                    product.product_id,
                    product.product_name,
                    product.price,
                    product.products_nature
                ))

                sql = "INSERT INTO Vendor_Sells_Product (vendor_id, product_id) VALUES (%s, %s)"
                cursor.execute(sql, (product.vendor_id, product.product_id))

            connection.commit()
            return {"message": "Product created successfully"}
        except Exception as e:
            raise e

    @staticmethod
    async def search_products(search_term: str):
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                sql = """SELECT * FROM Products
                        WHERE product_name LIKE %s
                        OR products_nature LIKE %s"""
                search_pattern = f"%{search_term}%"
                cursor.execute(sql, (search_pattern, search_pattern))
                return cursor.fetchall()
        except Exception as e:
            raise e
