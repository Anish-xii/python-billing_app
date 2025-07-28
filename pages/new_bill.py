import os
import json
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from datetime import datetime
from db.database import DB_PATH
from utils.pdf_utils import export_bill_pdf  

# Save bill to database
def save_bill_version(bill_id, total, items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT MAX(version_number) FROM bill_versions WHERE bill_id = ?", (bill_id,))
    current_max = c.fetchone()[0]
    next_version = (current_max or 0) + 1

    item_dicts = [{"code": code, "name": name, "qty": qty, "price": price} for code, name, qty, price in items]

    c.execute(
        "INSERT INTO bill_versions (bill_id, version_number, saved_at, total_amount, items) VALUES (?, ?, datetime('now'), ?, ?)",
        (bill_id, next_version, total, json.dumps(item_dicts))
    )

    conn.commit()
    conn.close()




class NewBillPage(tk.Frame):
    def __init__(self, parent, on_nav, bill_id=None):
        super().__init__(parent, bg="#1e1e1e")
        self.on_nav = on_nav
        self.bill_id = bill_id
        self.items = []
        self.inputs = {}
        self.original_state = None
        self.edit_index = None

        self.build_ui()
        if bill_id:
            self.load_existing_bill(bill_id)

    # -- UI LAYOUT ------------------------------------------------------------------------

    def build_ui(self):
        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True)
        # 60-40 SPLIT OF SCREEN
        left = tk.Frame(container, width=600, bg="#1e1e1e")
        right = tk.Frame(container, width=400, bg="#121212")
        left.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="y")
    
        self.build_left_section(left)
        self.build_right_section(right)


    def build_left_section(self, left):
        # Header
        tk.Label(left, text="🧾 New Bill", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        form = tk.Frame(left, bg="#1e1e1e")
        form.pack(pady=5, padx=20, anchor="w")

        # Customer Details
        for i, (label, key) in enumerate([("Name", "name"), ("Phone", "phone"), ("Address", "address")]):
            tk.Label(form, text=label, fg="white", bg="#1e1e1e").grid(row=i, column=0, sticky="e", pady=8)
            entry = tk.Entry(form, width=40, bg="#2a2a2a", fg="white", insertbackground="white")
            entry.grid(row=i, column=1, padx=10)
            self.inputs[key] = entry

        # Add Product Section
        prod_frame = tk.LabelFrame(left, text="➕ Add Product", bg="#1e1e1e", fg="white")
        prod_frame.pack(fill="x", padx=20, pady=17)

        tk.Label(prod_frame, text="Code", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)
        tk.Label(prod_frame, text="Name", bg="#1e1e1e", fg="white").grid(row=0, column=1, padx=5)
        tk.Label(prod_frame, text="Qty", bg="#1e1e1e", fg="white").grid(row=0, column=2, padx=5)
        tk.Label(prod_frame, text="Price", bg="#1e1e1e", fg="white").grid(row=0, column=3, padx=5)

        self.prod_code = tk.Entry(prod_frame, width=10)
        self.prod_name = tk.Entry(prod_frame, width=20)
        self.prod_qty = tk.Entry(prod_frame, width=5)
        self.prod_price = tk.Entry(prod_frame, width=7)

        self.prod_code.grid(row=1, column=0, padx=5, pady=(0, 8))
        self.prod_name.grid(row=1, column=1, padx=5, pady=(0, 8))
        self.prod_qty.grid(row=1, column=2, padx=5, pady=(0, 8))
        self.prod_price.grid(row=1, column=3, padx=5, pady=(0, 8))
        
        # -- Add Button --
        tk.Button(prod_frame, text="Add", command=self.add_item).grid(row=1, column=4, padx=5, pady=(0, 8))
        self.prod_code.bind("<FocusOut>", self.autofill_product)
        self.prod_name.bind("<FocusOut>", self.autofill_product)

        # Item preview Section (editable)
        self.total_label = tk.Label(left, text="Total: ₹0.00", font=("Arial", 12, "bold"), fg="white", bg="#1e1e1e")
        self.total_label.pack(pady=(5, 0))
        self.item_list = tk.Text(left, height=6, state="disabled", bg="#121212", fg="white")
        self.item_list.pack(fill="x", padx=20)
        self.item_list.bind("<Button-1>", self.select_item_for_edit)

        # Buttons (navigation, confirmation, delition)
        btn_frame = tk.Frame(left, bg="#1e1e1e")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="⬅ Go Back",
            command=lambda: self.on_nav("home"),
            bg="#333", fg="black",
            activebackground="#333", activeforeground="black"
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="✅ Confirm Bill",
            command=self.save_bill,
            bg="#007acc", fg="black",
            activebackground="#007acc", activeforeground="black"
        ).pack(side="left", padx=5)

        if self.bill_id:
            tk.Button(
                btn_frame, text="🗑 Delete Bill",
                command=self.delete_bill,
                bg="#aa3333", fg="black",
                activebackground="#aa3333", activeforeground="black"
            ).pack(side="left", padx=5)


    def build_right_section(self, right):
        header = tk.Frame(right, bg="#121212")
        header.pack(fill="x")
        tk.Label(header, text="🧾 Bill Preview", font=("Arial", 12, "bold"), bg="#121212", fg="white").pack(side="left", padx=10, pady=10)
        tk.Button(header, text="📥 Download PDF", command=self.download_pdf, bg="#444", fg="black").pack(side="right", padx=10)

        if self.bill_id:
            tk.Button(header, text="View History", command=self.show_history, bg="#444", fg="black").pack(side="right", padx=5)

        self.preview = tk.Text(right, state="disabled", bg="#181818", fg="white", height=20)
        self.preview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if self.bill_id:
            self.log_box = tk.Text(right, state="disabled", height=6, bg="#1e1e1e", fg="#bbbbbb")
            self.log_box.pack(fill="x", padx=10, pady=5)
            self.load_logs()



    # -- All FUNCTIONS -----------------------------------------

    def autofill_product(self, event=None):
        # Get user input
        code = self.prod_code.get().strip()
        name = self.prod_name.get().strip()
        # Connect to Database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # if (code/name) is entered + if product exist: Autofill (name/code) + price
        if code:
            c.execute("SELECT product_name, default_price FROM products WHERE product_code = ?", (code,))
            row = c.fetchone()
            if row:
                if not name:
                    self.prod_name.delete(0, tk.END)
                    self.prod_name.insert(0, row[0])
                if not self.prod_price.get():
                    self.prod_price.insert(0, str(row[1]))
        elif name:
            c.execute("SELECT product_code, default_price FROM products WHERE product_name = ?", (name,))
            row = c.fetchone()
            if row:
                if not code:
                    self.prod_code.insert(0, row[0])
                if not self.prod_price.get():
                    self.prod_price.insert(0, str(row[1]))

        conn.close()


    def add_item(self):
        # Take product details
        code = self.prod_code.get().strip()
        name = self.prod_name.get().strip()

        # Check valid qty price
        try:
            qty = int(self.prod_qty.get())
            price = float(self.prod_price.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity and Price must be numbers.")
            return

        if not name or qty <= 0:
            return

        # Make an item tuple (bundle of info)
        new_item = (code, name, qty, price)
        
        # if not editing existing bundle, append new bundle, else replace with new
        if self.edit_index is not None:
            self.items[self.edit_index] = new_item
            self.edit_index = None
        else:
            self.items.append(new_item)

        # Save to DB if new
        if code and name:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO products (product_code, product_name, default_price) VALUES (?, ?, ?)",
                      (code, name, price))
            conn.commit()
            conn.close()

        self.clear_inputs()
        self.update_preview()


    # if selected a valid bundle in preview, make the values of that bundle reasignable by add_item()
    def select_item_for_edit(self, event):
        try:
            index = self.item_list.index(f"@{event.x},{event.y}")
            line_num = int(str(index).split('.')[0]) - 1
            if 0 <= line_num < len(self.items):
                code, name, qty, price = self.items[line_num]
                self.prod_code.delete(0, tk.END); self.prod_code.insert(0, code)
                self.prod_name.delete(0, tk.END); self.prod_name.insert(0, name)
                self.prod_qty.delete(0, tk.END); self.prod_qty.insert(0, str(qty))
                self.prod_price.delete(0, tk.END); self.prod_price.insert(0, str(price))
                self.edit_index = line_num
        except Exception as e:
            print(f"[Edit Click Error] {e}")



    def clear_inputs(self):
        for entry in [self.prod_code, self.prod_name, self.prod_qty, self.prod_price]:
            entry.delete(0, tk.END)

    def update_preview(self):
        total = sum(q * p for _, _, q, p in self.items)
        self.total_label.config(text=f"Total: ₹{total:.2f}")

        self.item_list.config(state="normal")
        self.item_list.delete(1.0, tk.END)
        for i, (code, name, qty, price) in enumerate(self.items, 1):
            self.item_list.insert(tk.END, f"{i}. {name} (x{qty}) - ₹{price:.2f} = ₹{qty*price:.2f}\n")
        self.item_list.config(state="disabled")

        self.preview.config(state="normal")
        self.preview.delete(1.0, tk.END)
        self.preview.insert(tk.END, f"Customer: {self.inputs['name'].get()}\nPhone: {self.inputs['phone'].get()}\nAddress: {self.inputs['address'].get()}\n\n")
        for i, (code, name, qty, price) in enumerate(self.items, 1):
            self.preview.insert(tk.END, f"{i}. {name} (x{qty}) - ₹{price:.2f} = ₹{qty*price:.2f}\n")
        self.preview.insert(tk.END, f"\nTotal: ₹{total:.2f}")
        self.preview.config(state="disabled")


    def save_bill(self):
        name = self.inputs["name"].get()
        phone = self.inputs["phone"].get()
        address = self.inputs["address"].get()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(q * p for _, _, q, p in self.items)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if self.bill_id:
            c.execute("UPDATE bills SET customer_name=?, phone=?, address=?, date=?, total_amount=? WHERE id=?",
                      (name, phone, address, now, total, self.bill_id))
            c.execute("DELETE FROM bill_items WHERE bill_id=?", (self.bill_id,))
        else:
            c.execute("INSERT INTO bills (customer_name, phone, address, date, total_amount) VALUES (?, ?, ?, ?, ?)",
                      (name, phone, address, now, total))
            self.bill_id = c.lastrowid

        for code, name, qty, price in self.items:
            c.execute("INSERT INTO bill_items (bill_id, product_code, product_name, quantity, price) VALUES (?, ?, ?, ?, ?)",
                      (self.bill_id, code, name, qty, price))

        conn.commit()
        conn.close()

        if self.bill_id:
            save_bill_version(self.bill_id, total, self.items)

        messagebox.showinfo("Saved", "✅ Bill saved successfully!")
        self.on_nav("home")



    def delete_bill(self):
        if not self.bill_id:
            return

        if not messagebox.askyesno("Confirm", "⚠️ Are you sure you want to delete this bill?"):
            return

        def check_password():
            if password_entry.get() == "admin123":
                password_popup.destroy()
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM bills WHERE id=?", (self.bill_id,))
                c.execute("DELETE FROM bill_items WHERE bill_id=?", (self.bill_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "🗑 Bill deleted successfully.")
                self.on_nav("home")
            else:
                messagebox.showerror("Incorrect", "❌ Wrong password.")

        password_popup = tk.Toplevel(self)
        password_popup.title("Enter Password")
        password_popup.geometry("300x150")
        password_entry = tk.Entry(password_popup, show="*")
        tk.Label(password_popup, text="Enter password to delete bill:").pack(pady=10)
        password_entry.pack(pady=5)
        tk.Button(password_popup, text="Confirm", command=check_password, bg="red", fg="black").pack(pady=10)
        password_entry.focus_set()

    def load_existing_bill(self, bill_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT customer_name, phone, address FROM bills WHERE id=?", (bill_id,))
        row = c.fetchone()
        if row:
            self.inputs["name"].insert(0, row[0])
            self.inputs["phone"].insert(0, row[1])
            self.inputs["address"].insert(0, row[2])

        c.execute("SELECT product_code, product_name, quantity, price FROM bill_items WHERE bill_id=?", (bill_id,))
        self.items = c.fetchall()
        conn.close()

        self.update_preview()
        self.original_state = (row, self.items)

    def load_logs(self):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, "🔄 Change log for bill coming soon...")
        self.log_box.config(state="disabled")

    def show_history(self):
        window = tk.Toplevel(self)
        window.title("Bill Version History")
        window.geometry("700x400")

        tree = ttk.Treeview(window, columns=("version", "date", "total", "items"), show="headings")
        tree.heading("version", text="Version")
        tree.heading("date", text="Saved At")
        tree.heading("total", text="Total ₹")
        tree.heading("items", text="Items Snapshot")

        tree.column("version", width=80)
        tree.column("date", width=150)
        tree.column("total", width=80)
        tree.column("items", width=380)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT version_number, saved_at, total_amount, items FROM bill_versions WHERE bill_id = ? ORDER BY version_number DESC", (self.bill_id,))
        rows = c.fetchall()
        conn.close()

        for version, saved_at, total, items_json in rows:
            items = json.loads(items_json)
            item_str = ", ".join(f"{i['name']}({i['qty']})" for i in items)
            tree.insert("", "end", values=(version, saved_at, f"{total:.2f}", item_str))



    def download_pdf(self):
        if not self.bill_id:
            messagebox.showwarning("⚠️ No Bill", "Please save the bill before exporting to PDF.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT customer_name, phone, address, date FROM bills WHERE id=?", (self.bill_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("❌ Error", "Bill not found.")
            return

        bill_data = {
            "name": row[0],
            "phone": row[1],
            "address": row[2],
            "date": row[3]
        }

        c.execute("SELECT product_code, product_name, quantity, price FROM bill_items WHERE bill_id=?", (self.bill_id,))
        products = [
            {"code": code, "name": name, "qty": qty, "price": price}
            for code, name, qty, price in c.fetchall()
        ]
        conn.close()

        filename = os.path.join(str(Path.home() / "Downloads"), f"bill_{self.bill_id}.pdf")
        export_bill_pdf(bill_data, products, filename=filename)
        messagebox.showinfo("PDF Exported", f"📄 Bill PDF saved to Downloads.\n\n{filename}")
