from app.core.database import db

INIT_SQL = """
-- Create Vendors table
CREATE TABLE IF NOT EXISTS Vendors (
    vendor_id INT PRIMARY KEY,
    business_name VARCHAR(50) NOT NULL,
    customer_feedback_score INT,
    geographical_presence VARCHAR(100),
    inventory VARCHAR(100)
);

-- Create Products table
CREATE TABLE IF NOT EXISTS Products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    products_nature VARCHAR(100) NOT NULL
);

-- Create Customers table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT PRIMARY KEY,
    contact_number VARCHAR(50),
    shipping_details VARCHAR(100) NOT NULL
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create relationship: Vendor sells Product (Many-to-Many)
CREATE TABLE IF NOT EXISTS Vendor_Sells_Product (
    vendor_id INT,
    product_id INT,
    PRIMARY KEY (vendor_id, product_id),
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create relationship: Vendor involved in Transaction (Many-to-Many)
CREATE TABLE IF NOT EXISTS Vendor_Spans_Transaction (
    vendor_id INT,
    transaction_id INT,
    PRIMARY KEY (vendor_id, transaction_id),
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create relationship: Customer purchases Product (Many-to-Many)
CREATE TABLE IF NOT EXISTS Customer_Purchases_Product (
    customer_id INT,
    product_id INT,
    PRIMARY KEY (customer_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create relationship: Transaction includes Product (Many-to-Many)
CREATE TABLE IF NOT EXISTS Transaction_Details_Product (
    transaction_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create relationship: Customer performs Transaction (Many-to-Many)
CREATE TABLE IF NOT EXISTS Customer_Performs_Transaction (
    customer_id INT,
    transaction_id INT,
    PRIMARY KEY (customer_id, transaction_id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
"""

def init_db():
    """Initialize database tables"""
    try:
        # Split the SQL into individual statements
        statements = [s.strip() for s in INIT_SQL.split(';') if s.strip()]

        # Execute each statement
        for statement in statements:
            db.execute_query(statement)

        # Customer check
        print("INFO: Checking for existing customers...")
        count_result = db.execute_query("SELECT COUNT(*) as count FROM Customers")

        customer_count = 0
        if count_result and isinstance(count_result, list) and len(count_result) > 0 and isinstance(count_result[0], dict) and 'count' in count_result[0]:
            customer_count = count_result[0]['count']
            print(f"INFO: Found {customer_count} existing customers.")
        else:
            print("WARNING: Could not determine customer count. Proceeding cautiously.")
            customer_count = -1

        if customer_count == 0:
            print("INFO: No customers found. Adding default customer (ID: 1)...")
            default_customer_id = 1
            default_shipping_details = "N/A"

            insert_query = """
                INSERT INTO Customers (customer_id, shipping_details)
                VALUES (%s, %s)
            """
            try:
                insert_result = db.execute_query(insert_query, (default_customer_id, default_shipping_details))
                if insert_result.get("affected_rows", 0) > 0:
                    print(f"INFO: Default customer (ID: {default_customer_id}) added successfully.")
                else:
                    print(f"WARNING: Failed to add default customer (ID: {default_customer_id}). Insert reported 0 affected rows (maybe already exists?).")
            except Exception as insert_e:
                 print(f"ERROR: Failed during default customer insert: {insert_e}")
        elif customer_count > 0:
            print("INFO: Customers already exist. Skipping default customer creation.")
            
        return {"message": "Database initialized successfully"}
    except Exception as e:
        raise Exception(f"Database initialization failed: {str(e)}")
