from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.database import init_db
from data.sample_data_generator import generate_sample_data
from ingestion.transaction_loader import load_transactions
from ingestion.sanctions_loader import load_sanctions
from ingestion.pdf_processor import ingest_regulations
from rag.vector_store import build_index

if __name__ == "__main__":
    generate_sample_data()
    connection = init_db()
    load_transactions(Path("data/transactions.csv"), connection)
    load_sanctions(Path("data/sanctions.csv"), connection)
    ingest_regulations(Path("data/regulations"))
    build_index()
    print("Seeded SQLite, sample files, and regulatory index")
