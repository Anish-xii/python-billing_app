import tkinter as tk
from tkinter import ttk
import sqlite3
from db.database import DB_PATH
from datetime import datetime

class HomePage(tk.Frame):
    def __init__(self, parent, on_nav):
        super().__init__(parent, bg="#1e1e1e")
        self.on_nav = on_nav
        self.build_ui()

    def build_ui(self):
        # = Header ===========
        header_frame = tk.Frame(self, bg="#1e1e1e")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
        tk.Label(
            header_frame,
            text="📋 All Bills",
            font=("Segoe UI", 22, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(side="left")
    
        action_frame = tk.Frame(header_frame, bg="#1e1e1e")
        action_frame.pack(side="right")


        # -- BUTTON STYLES --------------------------------------
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Dark.TButton",
            background="#2e2e2e",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0,
            focusthickness=0,
            relief="flat"
        )
        style.map("Dark.TButton",
            background=[("active", "#3a3a3a")],
            foreground=[("active", "#ffffff")]
        )

        style.configure("Primary.TButton",
            background="#007acc",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0,
            focusthickness=0,
            relief="flat"
        )
        style.map("Primary.TButton",
            background=[("active", "#005fa3")],
            foreground=[("active", "#ffffff")]
        )

        style.configure("Ash.TButton",
            background="#3b3b3b", 
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            relief="flat",
            borderwidth=0
        )
        style.map("Ash.TButton",
            background=[("active", "#4a4a4a")],
            foreground=[("active", "white")]
        )


        # -- NAVIGATION BUTTONS -----------------------------------
        ttk.Button(
            action_frame,
            text="📦 All Products",
            style="Dark.TButton",
            command=lambda: self.on_nav("products")
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            action_frame,
            text="➕ New Bill",
            style="Primary.TButton",
            command=lambda: self.on_nav("new")
        ).pack(side="left")


        # --- Search Bar -------------------------------------
        search_frame = tk.Frame(self, bg="#1e1e1e")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
    
        tk.Label(
            search_frame,
            text="🔍",
            bg="#1e1e1e",
            fg="#cccccc",
            font=("Segoe UI", 12)
        ).pack(side="left")
    
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=40,
            bg="#2a2a2a",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#007acc",
            highlightbackground="#444"
        )
        search_entry.pack(side="left", padx=10, ipady=6)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_bill_list())


        # --- Table Section -----------------------------------------
        self.table_frame = tk.Frame(self, bg="#1e1e1e")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=("Name", "Phone", "Date", "Total"),
            show="tree headings",
            selectmode="browse"
        )
        # TABLE CONTENTS
        self.tree.heading("#0", text="📁 Month", anchor="w")
        self.tree.heading("Name", text="Customer Name", anchor="w")
        self.tree.heading("Phone", text="Phone Number", anchor="w")
        self.tree.heading("Date", text="Bill Date", anchor="center")
        self.tree.heading("Total", text="Total Amount", anchor="e")

        self.tree.column("#0", width=180, anchor="w")
        self.tree.column("Name", width=220, anchor="w")
        self.tree.column("Phone", width=150, anchor="w")
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Total", width=120, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, side="left")

        # TABLE UPDATE + STYLING
        self.setup_styles()
        self.tree.bind("<Double-1>", self.open_selected_bill)
        self.refresh_bill_list()




    # -- TABLE STYLING -------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # CONTENT ROWS
        style.configure("Treeview",
                        background="#1e1e1e",
                        fieldbackground="#1e1e1e",
                        foreground="#ffffff",
                        rowheight=34,
                        font=("Segoe UI", 13),  
                        borderwidth=0)

        # TABLE HEADING
        style.configure("Treeview.Heading",
                        background="#2c2c2c",
                        foreground="#ffffff",
                        font=("Segoe UI", 13, "bold"),  
                        borderwidth=0)

        # SELECTED ROW
        style.map("Treeview",
                  background=[("selected", "#007acc")],
                  foreground=[("selected", "#ffffff")])

        self.tree.tag_configure("evenrow", background="#2a2a2a")
        self.tree.tag_configure("oddrow", background="#1e1e1e")




    # -- TABLE UPDATE ----------------------------------
    def refresh_bill_list(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # FETCH DETAILS BY QUERY / SEARCH INPUT (IF EXISTS)
        query = "SELECT id, customer_name, phone, date, total_amount FROM bills ORDER BY date DESC"
        c.execute(query)
        search_term = self.search_var.get().lower()

        # For every bill, sort the bills by date (if no date, asign default). By date asign bills to table,
        month_groups = {}
        for bill_id, name, phone, date_str, total in c.fetchall():
            if search_term and search_term not in name.lower() and search_term not in phone:
                continue

            if not date_str:
                date_str = "1970-01-01 00:00:00"
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            month_key = date_obj.strftime("%B %Y")
            row = (
                bill_id,
                name,
                phone,
                date_obj.strftime("%Y-%m-%d"),
                f"₹{total:.2f}" if total is not None else "₹0.00"
            )

            if month_key not in month_groups:
                month_groups[month_key] = []
            month_groups[month_key].append(row)

        conn.close()

        for month, rows in month_groups.items():
            parent = self.tree.insert("", "end", text=month, open=True)
            for i, (bill_id, name, phone, date, total) in enumerate(rows):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree.insert(parent, "end", iid=str(bill_id), values=(name, phone, date, total), tags=(tag,))



    # -- ON DOUBLE CLICK OPEN BILL BY ID ---------------
    def open_selected_bill(self, event):
        selected = self.tree.focus()
        if selected and self.tree.parent(selected):
            self.on_nav("new", bill_id=int(selected))
