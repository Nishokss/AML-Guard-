from database.database import init_db
from data.sample_data_generator import generate_sample_data
from ingestion.transaction_loader import load_transactions
from ingestion.sanctions_loader import load_sanctions
from agents.workflow import AMLWorkflow

def test_agent_handoff(tmp_path):
    generate_sample_data(); db = init_db(tmp_path / "test.db"); load_transactions("data/transactions.csv", db); load_sanctions("data/sanctions.csv", db)
    result = AMLWorkflow(db).run("Which transactions violate guidance?", "analyst", "AML_ANALYST")
    assert result["screening_findings"]; assert "Agent 2: Verification completed" in result["workflow"]
