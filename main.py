import tkinter as tk
from pages.home import HomePage
from pages.new_bill import NewBillPage
from pages.products_page import ProductsPage
from db.database import init_db

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧾 Smart Billing Platform")
        self.geometry("1000x650")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.current_page = None
        self.show_page("home")

    def show_page(self, name, **kwargs):
        if self.current_page:
            self.current_page.destroy()

        if name == "home":
            page = HomePage(self.container, self.show_page)
        elif name == "new":
            page = NewBillPage(self.container, self.show_page, **kwargs)
        elif name == "products":  # ✅ ADD THIS
            page = ProductsPage(self.container, self.show_page)    

        self.current_page = page
        self.current_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
