import sqlite3
import json
from db.database import DB_PATH
from datetime import datetime

def save_bill(bill_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if bill_data.get("id"):
        # 🔁 Existing Bill — Fetch current version
        c.execute("SELECT customer_name, phone, date, total_amount FROM bills WHERE id = ?", (bill_data["id"],))
        existing = c.fetchone()

        if existing:
            customer_name, phone, date_str, total = existing
            c.execute("SELECT product_name, quantity, price FROM bill_items WHERE bill_id = ?", (bill_data["id"],))
            items = [{"name": name, "qty": qty, "price": price} for name, qty, price in c.fetchall()]

            # 🔒 Log version before overwrite
            c.execute("SELECT MAX(version_number) FROM bill_versions WHERE bill_id = ?", (bill_data["id"],))
            current_version = c.fetchone()[0] or 0

            c.execute("""
                INSERT INTO bill_versions (
                    bill_id, version_number, saved_at, customer_name, phone, date, total_amount, items
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_data["id"],
                current_version + 1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                customer_name,
                phone,
                date_str,
                total,
                json.dumps(items)
            ))

        # 📝 Update bill
        c.execute("""
            UPDATE bills SET customer_name = ?, phone = ?, date = ?, total_amount = ?
            WHERE id = ?
        """, (
            bill_data["customer_name"],
            bill_data["phone"],
            bill_data["date"],
            bill_data["total_amount"],
            bill_data["id"]
        ))

        c.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_data["id"],))
        bill_id = bill_data["id"]

    else:
        # ➕ New Bill
        c.execute("""
            INSERT INTO bills (customer_name, phone, date, total_amount)
            VALUES (?, ?, ?, ?)
        """, (
            bill_data["customer_name"],
            bill_data["phone"],
            bill_data["date"],
            bill_data["total_amount"]
        ))
        bill_id = c.lastrowid

    # 💾 Save bill items
    for item in bill_data["items"]:
        c.execute("""
            INSERT INTO bill_items (bill_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (
            bill_id,
            item["name"],
            item["qty"],
            item["price"]
        ))

    conn.commit()
    conn.close()
