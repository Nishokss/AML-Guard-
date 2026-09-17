from database.database import init_db
from data.sample_data_generator import generate_sample_data
from ingestion.transaction_loader import load_transactions
from ingestion.sanctions_loader import load_sanctions, match_sanctions

def test_ingestion_and_matching(tmp_path):
    generate_sample_data(); connection = init_db(tmp_path / "test.db")
    assert load_transactions("data/transactions.csv", connection) == 200
    assert load_sanctions("data/sanctions.csv", connection) == 3
    assert match_sanctions("john smith", connection)["status"] == "Exact match"
