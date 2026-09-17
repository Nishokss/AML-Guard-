from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.database import init_db
from data.sample_data_generator import generate_sample_data
from ingestion.transaction_loader import load_transactions
from ingestion.sanctions_loader import load_sanctions
from agents.workflow import AMLWorkflow
from security.rbac import protect_customer_record
from config.roles import has_permission
from feedback.feedback_manager import submit_feedback, adjusted_finding
from ingestion.pdf_processor import ingest_regulations
from rag.vector_store import build_index
from app import customer_response

def run():
    generate_sample_data(); db = init_db(":memory:"); load_transactions("data/transactions.csv", db); load_sanctions("data/sanctions.csv", db)
    ingest_regulations("data/regulations"); build_index()
    cases = json.loads((Path(__file__).with_name("evaluation_questions.json")).read_text()); passed = 0
    for case in cases:
        kind = case["test_type"]; result = AMLWorkflow(db).run(case["question"], "eval", case["role"])
        ok = bool(result.get("screening_findings")) if kind in {"screening", "combined"} else True
        if kind == "sanctions": ok = any(f["sanctions_match"]["status"] != "No match" for f in result["screening_findings"])
        if kind == "rag": ok = any(f["regulatory_evidence"] for f in result["screening_findings"])
        if kind == "handoff": ok = "Agent 2: Verification completed" in result["workflow"]
        if kind in {"analyst_refusal", "auditor_refusal"}: ok = not has_permission(case["role"], "customer_pii")
        if kind == "pii": ok = protect_customer_record(case["role"], {"name":"John Smith"})[1]["name"] != "John Smith"
        if kind == "admin_access": ok = protect_customer_record(case["role"], {"name":"John Smith"})[1]["name"] == "John Smith"
        if kind == "role_behavior": ok = "audit_logs" in __import__("config.roles", fromlist=["PERMISSIONS"]).PERMISSIONS[case["role"]]
        if kind == "portfolio_access":
            result = customer_response(case["question"], "relationship_manager", case["role"], db)
            ok = result["access_decision"] == "ALLOWED" and result["customer"]["sender_name"] != "John Smith"
        if kind == "portfolio_refusal":
            result = customer_response(case["question"], "relationship_manager", case["role"], db)
            ok = result == {"answer": "ACCESS DENIED", "access_decision": "DENIED"}
        if kind == "portfolio_screening":
            ok = bool(result["screening_findings"]) and all(f["customer_id"] <= "C010" for f in result["screening_findings"])
        if kind == "feedback":
            finding = {"transaction_id":"T999", "risk_score":80, "risk_level":"HIGH"}; submit_feedback(db, 1, "T999", "FALSE POSITIVE", "test", "eval"); ok = adjusted_finding(finding, db)["risk_score"] == 60
        passed += int(ok); print(f"{case['id']} {'PASS' if ok else 'FAIL'}")
    print(f"PASS RATE: {passed / len(cases) * 100:.0f}%")
    return passed == len(cases)

if __name__ == "__main__": raise SystemExit(0 if run() else 1)
