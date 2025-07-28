import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from db.database import DB_PATH

class ProductsPage(tk.Frame):
    def __init__(self, parent, on_nav):
        super().__init__(parent)
        self.on_nav = on_nav
        self.build_ui()
        self.load_products()


    def build_ui(self):
        self.configure(bg="#1e1e1e")

        # -- Button designs -----
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Primary.TButton",
                        background="#007acc",
                        foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        borderwidth=0,
                        relief="flat")
        style.map("Primary.TButton",
                  background=[("active", "#005fa3")])

        style.configure("Dark.TButton",
                        background="#2e2e2e",
                        foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        borderwidth=0,
                        relief="flat")
        style.map("Dark.TButton",
                  background=[("active", "#3a3a3a")])

        style.configure("Ash.TButton",
            background="#262525",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0,
            relief="flat"
        )
        style.map("Ash.TButton",
            background=[("active", "#4a4a4a")]
        )

        # Header
        header = tk.Label(self, text="📦 All Products", font=("Segoe UI", 20, "bold"),
                          bg="#1e1e1e", fg="#ffffff")
        header.pack(pady=(20, 10))

        #  Buttons 
        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(pady=(0, 10))

        ttk.Button(
            btn_frame,
            text="➕ Add Product",
            style="Primary.TButton",
            command=self.add_product_popup
        ).pack()

        # Scrollable Table
        style.configure("Treeview",
            background="#1e1e1e",
            foreground="white",
            rowheight=30,
            fieldbackground="#1e1e1e",
            font=("Segoe UI", 13),
            borderwidth=0
        )
        style.map("Treeview",
            background=[("selected", "#007acc")],
            foreground=[("selected", "white")]
        )

        style.configure("Treeview.Heading",
            background="#2e2e2e",
            foreground="white",
            font=("Segoe UI", 13, "bold"),
            relief="flat"
        )

        style.layout("Treeview.Heading", [
            ('Treeheading.cell', {'sticky': 'nswe'}),
            ('Treeheading.border', {'sticky': 'nswe', 'children': [
                ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                    ('Treeheading.image', {'side': 'right', 'sticky': ''}),
                    ('Treeheading.text', {'sticky': 'we'})
                ]})
            ]})
        ])

        #--
        tree_frame = tk.Frame(self, bg="#1e1e1e")
        tree_frame.pack(padx=20, pady=10, fill="x")

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("product_code", "product_name", "default_price")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=15,  # Fixed number of rows
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("product_code", text="Product Code")
        self.tree.heading("product_name", text="Product Name")
        self.tree.heading("default_price", text="Default Price")

        for col in columns:
            self.tree.column(col, anchor="w", width=200)

        self.tree.pack(side="left", fill="x", expand=True)


        # Menu on Double Click 
        self.menu = tk.Menu(self, tearoff=0, bg="#2a2a2a", fg="#ffffff", activebackground="#007acc", activeforeground="#ffffff")
        self.menu.add_command(label="✏️ Edit", command=self.edit_selected_product)
        self.menu.add_command(label="🗑️ Delete", command=self.delete_selected_product)
        self.tree.bind("<Double-1>", self.show_context_menu)

        # Back Button 
        ttk.Button(
            self,
            text="← Back",
            style="Dark.TButton",
            command=lambda: self.on_nav("home")
        ).pack(pady=(10, 20))



    # --- All functionalitys ----------------------------------

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT product_code, product_name, default_price FROM products ORDER BY product_name ASC")
        rows = c.fetchall()
        conn.close()

        for code, name, price in rows:
            self.tree.insert("", "end", values=(code, name, price))

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def add_product_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Product")
        popup.geometry("300x250")

        tk.Label(popup, text="Product Code").pack(pady=5)
        code_entry = tk.Entry(popup)
        code_entry.pack()

        tk.Label(popup, text="Product Name").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack()

        tk.Label(popup, text="Default Price").pack(pady=5)
        price_entry = tk.Entry(popup)
        price_entry.pack()



        def save():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            try:
                price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid", "Price must be a number")
                return

            if not code or not name:
                messagebox.showerror("Missing", "Please fill all fields")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO products (product_code, product_name, default_price) VALUES (?, ?, ?)",
                          (code, name, price))
                conn.commit()
                messagebox.showinfo("Success", "Product added successfully!")
                popup.destroy()
                self.load_products()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Product code already exists.")
            finally:
                conn.close()

        ttk.Button(popup, text="Save Product", command=save, style="Ash.TButton").pack(pady=10)



    def edit_selected_product(self):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        code, name, price = values

        form = tk.Toplevel(self)
        form.title(f"Edit Product {code}")
        form.geometry("300x250")

        tk.Label(form, text="Product Code").pack(pady=5)
        code_entry = tk.Entry(form)
        code_entry.insert(0, code)
        code_entry.config(state='disabled')
        code_entry.pack()

        tk.Label(form, text="Product Name").pack(pady=5)
        name_entry = tk.Entry(form)
        name_entry.insert(0, name)
        name_entry.pack()

        tk.Label(form, text="Default Price").pack(pady=5)
        price_entry = tk.Entry(form)
        price_entry.insert(0, str(price))
        price_entry.pack()



        def save():
            new_name = name_entry.get().strip()
            try:
                new_price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid", "Price must be a number")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE products SET product_name = ?, default_price = ? WHERE product_code = ?",
                      (new_name, new_price, code))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_products()
            messagebox.showinfo("Updated", "Product updated successfully.")

        ttk.Button(form, text="Save Changes", command=save, style="Ash.TButton").pack(pady=10)



    def delete_selected_product(self):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        code = values[0]

        confirm = messagebox.askyesno("Confirm Delete", f"Delete product {code}?")
        if confirm:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE product_code = ?", (code,))
            conn.commit()
            conn.close()
            self.load_products()
            messagebox.showinfo("Deleted", "Product deleted.")
