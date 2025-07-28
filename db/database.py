import sqlite3
import os

DB_PATH = "db/billing.db"

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Bills table
    c.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            address TEXT,
            date TEXT,
            total_amount REAL
        )
    """)

    # Bill items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            product_code TEXT,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    """)

    # Products table
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE,
            product_name TEXT,
            default_price REAL
        )
    """)

     # New: bill_versions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS bill_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        version_number INTEGER,
        saved_at TEXT,
        customer_name TEXT,
        phone TEXT,
        date TEXT,
        total_amount REAL,
        items TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")

if __name__ == "__main__":
    init_db()
