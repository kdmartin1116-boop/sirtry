from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("utility_bill.pdf", pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Alabama Power")
c.drawString(100, 730, "Electric Service for July 2025")
c.drawString(100, 710, "Amount Due: $142.87")
c.drawString(100, 690, "Account Number: 123456789")
c.save()

print("✅ Dummy utility_bill.pdf created.")