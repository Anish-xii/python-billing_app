# AI degigned pdf structuer
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def export_bill_pdf(bill_data, products, filename="bill.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    margin_x = 50
    y = height - 50

    # === Header ===
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin_x, y, "● Customer Invoice")
    y -= 30

    # === Bill Info ===
    c.setFont("Helvetica", 11)
    c.drawString(margin_x, y, f"Name     : {bill_data['name']}")
    y -= 18
    c.drawString(margin_x, y, f"Phone    : {bill_data['phone']}")
    y -= 18
    c.drawString(margin_x, y, f"Address  : {bill_data['address']}")
    y -= 18
    c.drawString(margin_x, y, f"Date     : {bill_data['date']}")
    y -= 30

    # === Table Header ===
    c.setFont("Helvetica-Bold", 12)
    headers = ["Code", "Product", "Qty", "Price", "Total"]
    col_x = [margin_x, margin_x + 80, margin_x + 300, margin_x + 360, margin_x + 430]

    for i, header in enumerate(headers):
        c.drawString(col_x[i], y, header)
    y -= 5
    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # === Table Rows ===
    c.setFont("Helvetica", 11)
    grand_total = 0

    for item in products:
        total = item['qty'] * item['price']
        grand_total += total

        row_data = [
            str(item['code']),
            item['name'],
            str(item['qty']),
            f"₹ {item['price']:.2f}",
            f"₹ {total:.2f}"
        ]

        for i, data in enumerate(row_data):
            c.drawString(col_x[i], y, data)

        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    # === Grand Total ===
    y -= 10
    c.line(margin_x, y, width - margin_x, y)
    y -= 25
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - margin_x, y, f"Grand Total: ₹ {grand_total:.2f}")
    y -= 40

    # === Footer ===
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 30, "Thank you for your business!")
    c.setFillColor(colors.black)

    c.save()
