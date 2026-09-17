class InvestigationAgent:
    def __init__(self, connection): self.connection = connection
    def run(self, screening_findings, question=""):
        verified = []
        for finding in screening_findings:
            evidence = finding.get("regulatory_evidence", [])
            supported = bool(evidence)
            reasons = list(finding.get("reasons", []))
            verified.append({**finding, "verified": supported, "verification": "Supported by retrieved demo regulatory evidence." if supported else "Insufficient regulatory evidence found.", "final_priority": finding["risk_level"] if supported else "REVIEW"})
        return {"verified_findings": verified, "final_answer": self._answer(verified, question)}
    def _answer(self, findings, question):
        if not findings: return "No suspicious transactions were found in the permitted dataset."
        if not any(item["verified"] for item in findings): return "Insufficient regulatory evidence found."
        return f"Screening identified {len(findings)} potentially suspicious transaction(s). Findings are supported by retrieved regulatory evidence and require analyst review."
