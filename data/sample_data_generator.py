from pathlib import Path
from datetime import date, timedelta
import csv
import random

ROOT = Path(__file__).resolve().parent

def generate_sample_data():
    ROOT.mkdir(exist_ok=True)
    transactions = []
    names = ["John Smith", "Priya Shah", "Lina Chen", "Arun Kumar", "Maria Garcia", "David Brown"]
    countries = ["India", "United Kingdom", "Singapore", "United States", "Iran", "United Arab Emirates"]
    today = date.today()
    for index in range(1, 201):
        suspicious = index % 17 == 0
        amount = (1500000 + index * 1000) if suspicious else (5000 + (index * 137) % 90000)
        customer = f"C{((index - 1) % 20) + 1:03d}"
        sender = "John Smith" if index in (17, 34, 51) else names[index % len(names)]
        description = "Urgent transfer for invoice" if not suspicious else "urgent cash transfer, bypass compliance review"
        transactions.append({"transaction_id": f"T{index:03d}", "customer_id": customer, "amount": amount, "country": "Iran" if suspicious and index % 2 else countries[index % len(countries)], "date": (today - timedelta(days=index % 35)).isoformat(), "sender_name": sender, "receiver_name": names[(index + 2) % len(names)], "description": description, "risk_score": 0})
    with (ROOT / "transactions.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=transactions[0].keys())
        writer.writeheader(); writer.writerows(transactions)
    sanctions = [{"name": "John Smith", "entity_type": "PERSON", "country": "United Kingdom", "sanctions_program": "DEMO-WATCHLIST"}, {"name": "Acme Trading Ltd", "entity_type": "ORGANIZATION", "country": "Iran", "sanctions_program": "DEMO-WATCHLIST"}, {"name": "Lina Chen", "entity_type": "PERSON", "country": "Singapore", "sanctions_program": "DEMO-WATCHLIST"}]
    with (ROOT / "sanctions.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sanctions[0].keys())
        writer.writeheader(); writer.writerows(sanctions)
    regulations = ROOT / "regulations"; regulations.mkdir(exist_ok=True)
    guidance = "DEMO/SAMPLE REGULATORY MATERIAL - not official legal advice\n\nSection 4: Customer due diligence\nFinancial institutions should understand the nature and purpose of customer relationships and apply risk-based monitoring.\n\nSection 7: Correspondent banking\nInstitutions should assess correspondent banking relationships, identify risks, and maintain enhanced controls for higher-risk relationships.\n\nSection 9: Suspicious activity\nUnusual transaction patterns, rapid movement of funds, large transfers, and activity involving high-risk jurisdictions should receive further review and appropriate reporting consideration."
    (regulations / "demo_aml_guidance.txt").write_text(guidance, encoding="utf-8")
    try:
        from reportlab.pdfgen import canvas
        pdf = canvas.Canvas(str(regulations / "demo_aml_guidance.pdf")); pdf.setFont("Helvetica", 10)
        for line_number, line in enumerate(guidance.splitlines()):
            pdf.drawString(48, 780 - (line_number % 45) * 15, line[:110])
            if line_number and line_number % 45 == 0: pdf.showPage(); pdf.setFont("Helvetica", 10)
        pdf.save()
    except ImportError:
        pass

if __name__ == "__main__":
    generate_sample_data(); print("Generated 200 transactions, sanctions, and demo regulation")
