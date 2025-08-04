# 🧾 Billing App – Desktop Invoicing System (Tkinter + SQLite)

A lightweight desktop billing platform built using Python’s `Tkinter` for the GUI and `SQLite` for local data management. Ideal for small businesses and freelancers who need a fast, offline billing tool with invoice generation, product autofill, and PDF exports — all without relying on Excel or online platforms.

---

## ✨ Features

- **Create & Preview Bills** with live total calculation
- **Download Bills as PDF** in a clean, printable format
-  **Smart Product Autofill** from saved products list
-  **Edit Existing Bills** with versioned history
- �**Product Management Page** – add, update, or delete items
-  **Delete Protection** – optional admin prompt for dangerous actions
-  **SQLite Storage** – local, portable, no setup required
-  **Clean UI Design** – dual-panel layout for input and preview

---

## 🛠️ Tech Stack

| Layer        | Technology       |
|--------------|------------------|
| UI           | Python `Tkinter` |
| Database     | SQLite (`.db`)   |
| Export       | PDF (via `reportlab` or similar) |
| Architecture | Modular + OOP    |
| Packaging    | `PyInstaller` (optional executable build)

---

## 📸 Screenshots

**Home page**
<img width="989" height="642" alt="Screenshot 2025-08-04 at 15 10 12" src="https://github.com/user-attachments/assets/8365506a-8657-4f96-958b-bfe6a1162c41" />

**All products page**
<img width="989" height="642" alt="Screenshot 2025-08-04 at 15 05 42" src="https://github.com/user-attachments/assets/900d9e95-74f2-40b9-957b-0d316c7f18e8" />

**Bill page**
<img width="989" height="642" alt="Screenshot 2025-08-04 at 15 01 31" src="https://github.com/user-attachments/assets/1051fcd4-b334-4b01-870a-8f93acdd6e9b" />

**Bill History**
 <img width="989" height="642" alt="Screenshot 2025-08-04 at 15 10 24" src="https://github.com/user-attachments/assets/d57b1276-91f4-4ba2-8128-f156ee2208d5" />


---

##  Getting Started

###  Requirements

- Python 3.8+
- Required packages: install via pip

```bash
pip install -r requirements.txt

