import sqlite3
from db.database import DB_PATH

def fetch_product_by_code(code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, price FROM products WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def fetch_product_by_name(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, price FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def save_new_product(code, name, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO products (code, name, price) VALUES (?, ?, ?)",
        (code, name, price)
    )
    conn.commit()
    conn.close()
