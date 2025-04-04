from app.core.database import db, DatabaseError
from app.models.schemas import TransactionCreate
from typing import Dict, Any, List

class TransactionService:
    @staticmethod
    async def verify_products(products: List[Dict]) -> bool:
        """Verify if all products exist and are available"""
        try:
            for product in products:
                product_id = product['product_id']
                result = db.execute_query(
                    "SELECT COUNT(*) as count FROM Products WHERE product_id = %s",
                    (product_id,)
                )
                if result[0]['count'] == 0:
                    raise DatabaseError(f"Product with ID {product_id} does not exist")
            return True
        except Exception as e:
            raise DatabaseError(f"Product verification failed: {str(e)}")

    @staticmethod
    async def verify_customer(customer_id: int) -> bool:
        """Verify if customer exists"""
        try:
            result = db.execute_query(
                "SELECT COUNT(*) as count FROM Customers WHERE customer_id = %s",
                (customer_id,)
            )
            if result[0]['count'] == 0:
                raise DatabaseError(f"Customer with ID {customer_id} does not exist")
            return True
        except Exception as e:
            raise DatabaseError(f"Customer verification failed: {str(e)}")

    @staticmethod
    async def verify_vendors_for_products(products: List[Dict]) -> List[int]:
        """Get vendors associated with the products"""
        try:
            product_ids = [p['product_id'] for p in products]
            placeholders = ','.join(['%s'] * len(product_ids))
            query = f"""
                SELECT DISTINCT vendor_id
                FROM Vendor_Sells_Product
                WHERE product_id IN ({placeholders})
            """
            result = db.execute_query(query, tuple(product_ids))
            if not result:
                raise DatabaseError("No vendors found for the selected products")
            return [r['vendor_id'] for r in result]
        except Exception as e:
            raise DatabaseError(f"Vendor verification failed: {str(e)}")

    @staticmethod
    async def create_transaction(transaction_data: TransactionCreate) -> Dict[str, Any]:
        """Create a new transaction with validation"""
        try:
            # Verify customer exists
            await TransactionService.verify_customer(transaction_data.customer_id)

            # Verify all products exist
            await TransactionService.verify_products(transaction_data.products)

            # Get vendors for the products
            vendor_ids = await TransactionService.verify_vendors_for_products(transaction_data.products)

            # Start transaction
            connection = db.get_connection()
            try:
                with connection.cursor() as cursor:
                    # Create transaction
                    cursor.execute(
                        "INSERT INTO Transactions (transaction_date) VALUES (CURRENT_TIMESTAMP)"
                    )
                    transaction_id = cursor.lastrowid

                    # Link customer to transaction
                    cursor.execute(
                        """INSERT INTO Customer_Performs_Transaction
                           (customer_id, transaction_id) VALUES (%s, %s)""",
                        (transaction_data.customer_id, transaction_id)
                    )

                    # Add products to transaction
                    for product in transaction_data.products:
                        cursor.execute(
                            """INSERT INTO Transaction_Details_Product
                               (transaction_id, product_id, quantity)
                               VALUES (%s, %s, %s)""",
                            (transaction_id, product['product_id'], product.get('quantity', 1))
                        )

                    # Link vendors to transaction
                    for vendor_id in vendor_ids:
                        cursor.execute(
                            """INSERT INTO Vendor_Spans_Transaction
                               (vendor_id, transaction_id) VALUES (%s, %s)""",
                            (vendor_id, transaction_id)
                        )

                    connection.commit()
                    return {
                        "transaction_id": transaction_id,
                        "message": "Transaction created successfully",
                        "vendors": vendor_ids
                    }
            except Exception as e:
                connection.rollback()
                raise DatabaseError(f"Transaction creation failed: {str(e)}")
            finally:
                connection.close()
        except DatabaseError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"Unexpected error in transaction creation: {str(e)}")
