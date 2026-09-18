import json

from config.settings import DEMO_MODE, LLM_API_KEY, LLM_MODEL, LLM_PROVIDER


class InvestigationAgent:
    def __init__(self, connection): self.connection = connection
    def run(self, screening_findings, question="", use_llm=True):
        verified = []
        for finding in screening_findings:
            evidence = finding.get("regulatory_evidence", [])
            supported = bool(evidence)
            reasons = list(finding.get("reasons", []))
            verified.append({**finding, "verified": supported, "verification": "Supported by retrieved demo regulatory evidence." if supported else "Insufficient regulatory evidence found.", "final_priority": finding["risk_level"] if supported else "REVIEW"})
        return {"verified_findings": verified, "final_answer": self._answer(verified, question, use_llm)}
    def _answer(self, findings, question, use_llm=True):
        if not use_llm or DEMO_MODE or LLM_PROVIDER not in {"gemini", "groq"}:
            return self._deterministic_answer(findings, question)
        try:
            safe_findings = [
                {
                    "transaction_id": item["transaction_id"],
                    "date": item["date"],
                    "amount": item["amount"],
                    "country": item["country"],
                    "risk_level": item["risk_level"],
                    "risk_score": item["risk_score"],
                    "reasons": item["reasons"],
                    "sanctions_status": item["sanctions_match"]["status"],
                    "evidence": [evidence["text"][:400] for evidence in item["regulatory_evidence"][:2]],
                }
                for item in findings[:20]
            ]
            prompt = (
                "Answer the user's AML question directly using only the supplied findings and evidence. "
                "Explain the relevant transactions, risk reasons, sanctions status, and regulatory support. "
                "If the data does not answer the question, say so clearly. Do not invent facts, expose PII, "
                "or provide legal advice. Keep the answer concise and suitable for a compliance analyst.\n\n"
                f"User question: {question}\n"
                f"Findings: {json.dumps(safe_findings, default=str)}"
            )
            if LLM_PROVIDER == "groq":
                from groq import Groq
                response = Groq(api_key=LLM_API_KEY).chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are the real-time AML Assistant. Answer every user question from the supplied data.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_completion_tokens=1200,
                    reasoning_effort="low",
                )
                return response.choices[0].message.content.strip() or "Groq returned an empty response."
            from google import genai
            response = genai.Client(api_key=LLM_API_KEY).models.generate_content(model=LLM_MODEL, contents=prompt)
            return response.text.strip() or "Gemini returned an empty response."
        except Exception as error:
            provider_name = LLM_PROVIDER.title()
            return (
                f"{provider_name} could not generate the answer right now. "
                f"Check the {provider_name} API key, model access, and internet connection, then try again. "
                "The verified findings below are still available for review."
            )

    def _deterministic_answer(self, findings, question):
        if not findings:
            return "No suspicious transactions were found in the permitted dataset."
        question_lower = question.lower()
        if "sanction" in question_lower or "watchlist" in question_lower:
            matches = [item for item in findings if item["sanctions_match"]["status"] != "No match"]
            if not matches:
                return "No sanctions matches were found in the permitted dataset."
            transactions = ", ".join(item["transaction_id"] for item in matches[:10])
            return f"Found {len(matches)} transaction(s) with sanctions results: {transactions}. Review the matched parties before proceeding."
        if "above" in question_lower or "over" in question_lower or "greater" in question_lower:
            large = [item for item in findings if "Large transaction" in item["reasons"]]
            if not large:
                return "No suspicious transactions above the configured amount threshold were found."
            transactions = ", ".join(item["transaction_id"] for item in large[:10])
            return f"Found {len(large)} transaction(s) above the configured amount threshold: {transactions}."
        if "regulation" in question_lower or "fatf" in question_lower or "guidance" in question_lower or "evidence" in question_lower:
            supported = [item for item in findings if item.get("regulatory_evidence")]
            return f"Found {len(supported)} transaction(s) with retrieved regulatory evidence for review."
        verified = sum(bool(item.get("regulatory_evidence")) for item in findings)
        return f"Screening identified {len(findings)} potentially suspicious transaction(s); {verified} have supporting regulatory evidence and require analyst review."
