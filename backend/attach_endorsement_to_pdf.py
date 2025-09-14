import json
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

# Load endorsement chain
with open("remedy_logs/2025-08-18_WEB-UTIL-001.json", "r") as f:
    bill = json.load(f)

# Create overlay PDF with endorsement text
packet = BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
can.setFont("Helvetica-Bold", 12)
can.drawString(50, 750, "🔗 Endorsement Chain Attached")

can.setFont("Helvetica", 10)
y = 730
for i, e in enumerate(bill.get("endorsements", []), start=1):
    can.drawString(50, y, f"{i}. {e['endorser_name']} → {e['next_payee']}")
    y -= 15
    can.drawString(60, y, f"Text: {e['text']}")
    y -= 15
    can.drawString(60, y, f"Signature: {e['signature'][:60]}...")
    y -= 25

sig = bill.get("signature_block", {})
can.drawString(50, y, f"Signed by: {sig.get('signed_by')} ({sig.get('capacity')})")
y -= 15
can.drawString(60, y, f"Signature: {sig.get('signature')}")
y -= 15
can.drawString(60, y, f"Date: {sig.get('date')}")
can.save()
packet.seek(0)

# Load original PDF
reader = PdfReader("utility_bill.pdf")
writer = PdfWriter()
overlay = PdfReader(packet)

# Merge overlay onto first page
page = reader.pages[0]
page.merge_page(overlay.pages[0])
writer.add_page(page)

# Add remaining pages
for p in reader.pages[1:]:
    writer.add_page(p)

# Save new PDF
with open("endorsed_utility_bill.pdf", "wb") as f:
    writer.write(f)

print("📎 Endorsement chain attached to endorsed_utility_bill.pdf")