from app.core.database import db
from app.models.schemas import VendorCreate

class VendorService:
    @staticmethod
    async def get_all_vendors():
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Vendors"
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            raise e

    @staticmethod
    async def create_vendor(vendor: VendorCreate):
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                sql = """INSERT INTO Vendors
                        (vendor_id, business_name, customer_feedback_score,
                         geographical_presence, inventory)
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    vendor.vendor_id,
                    vendor.business_name,
                    vendor.customer_feedback_score,
                    vendor.geographical_presence,
                    vendor.inventory
                ))
            connection.commit()
            return {"message": "Vendor created successfully"}
        except Exception as e:
            raise e
