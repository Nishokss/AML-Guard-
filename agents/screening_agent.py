from collections import defaultdict
from datetime import date
import json
from config.settings import LARGE_TRANSACTION_THRESHOLD, HIGH_RISK_COUNTRIES
from ingestion.sanctions_loader import match_sanctions
from rag.retriever import retrieve_regulatory_evidence

class ScreeningAgent:
    def __init__(self, connection, large_threshold=LARGE_TRANSACTION_THRESHOLD):
        self.connection = connection; self.large_threshold = large_threshold
    def run(self, question="", limit=100, customer_ids=None):
        query = "SELECT * FROM transactions"
        parameters = []
        if customer_ids is not None:
            if not customer_ids:
                return []
            placeholders = ",".join("?" for _ in customer_ids)
            query += f" WHERE customer_id IN ({placeholders})"
            parameters.extend(sorted(customer_ids))
        query += " ORDER BY date DESC LIMIT ?"
        parameters.append(limit)
        transactions = [dict(row) for row in self.connection.execute(query, parameters).fetchall()]
        counts = defaultdict(int)
        for item in transactions: counts[item["customer_id"]] += 1
        findings = []
        for transaction in transactions:
            reasons = []
            if float(transaction["amount"]) >= self.large_threshold: reasons.append("Large transaction")
            if str(transaction["country"]).upper() in HIGH_RISK_COUNTRIES: reasons.append("High-risk country")
            if counts[transaction["customer_id"]] >= 8: reasons.append("Repeated transaction pattern")
            if any(word in str(transaction["description"]).lower() for word in ("urgent", "bypass", "cash")): reasons.append("Unusual transaction narrative")
            sanctions = match_sanctions(transaction["sender_name"], self.connection)
            if sanctions["status"] != "No match": reasons.append(f"{sanctions['status']} sanctions result")
            base_score = min(100, len(reasons) * 20 + (30 if float(transaction["amount"]) >= self.large_threshold else 0))
            if reasons:
                findings.append({"transaction_id": transaction["transaction_id"], "customer_id": transaction["customer_id"], "date": transaction["date"], "amount": transaction["amount"], "country": transaction["country"], "risk_level": "HIGH" if base_score >= 70 else "MEDIUM", "risk_score": base_score, "reasons": reasons, "sanctions_match": sanctions, "regulatory_evidence": retrieve_regulatory_evidence(question or "suspicious transaction high risk monitoring", 2)})
        return findings
