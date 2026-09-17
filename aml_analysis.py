"""AML Compliance Assistant analysis workflow.

Run from the project root with: python aml_analysis.py
This file can also be opened in VS Code and run cell-by-cell using # %% cells.
The Streamlit interface remains in app.py.
"""
# %%
from pathlib import Path
import json
import subprocess
import sys

import pandas as pd

try:
    from IPython.display import display
except ImportError:
    def display(value):
        print(value)

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.workflow import AMLWorkflow
from data.sample_data_generator import generate_sample_data
from database.database import init_db
from feedback.feedback_manager import adjusted_finding, submit_feedback
from ingestion.pdf_processor import ingest_regulations
from ingestion.sanctions_loader import load_sanctions
from ingestion.transaction_loader import load_transactions
from rag.retriever import retrieve_regulatory_evidence
from rag.vector_store import build_index
from security.rbac import protect_customer_record

# %%
# Prepare the predefined demo dataset in an isolated in-memory database.
generate_sample_data()
db = init_db(":memory:")
transaction_count = load_transactions(ROOT / "data" / "transactions.csv", db)
sanction_count = load_sanctions(ROOT / "data" / "sanctions.csv", db)
regulatory_chunks = ingest_regulations(ROOT / "data" / "regulations")
build_index()
print(f"Loaded {transaction_count} transactions, {sanction_count} sanctions, {len(regulatory_chunks)} regulatory chunks")

# %%
# Inspect the input data.
transactions = pd.read_sql_query("SELECT * FROM transactions LIMIT 10", db)
sanctions = pd.read_sql_query("SELECT name, entity_type, country FROM sanctions", db)
display(transactions)
display(sanctions)

# %%
# Run the complete RBAC -> Screening -> Investigation workflow.
question = "Which transactions violate AML guidance?"
workflow_result = AMLWorkflow(db).run(question, "analyst", "AML_ANALYST")
print(workflow_result["final_answer"])
print("Workflow:", " -> ".join(workflow_result["workflow"]))
findings = workflow_result["verification"]
display(pd.DataFrame(findings)[["transaction_id", "risk_level", "risk_score", "country", "reasons"]].head(20))

# %%
# Show regulatory RAG evidence used for the analysis.
evidence = retrieve_regulatory_evidence("correspondent banking suspicious transaction monitoring")
for item in evidence:
    print(f"{item['document_name']} | page {item['page_number']} | {item['text']}")

# %%
# Demonstrate backend-enforced role-specific PII access.
customer = {"customer_id": "C001", "name": "John Smith", "phone": "9876543210", "address": "Private address"}
for role in ("ADMIN", "AML_ANALYST", "EXTERNAL_AUDITOR"):
    permitted, safe_record = protect_customer_record(role, customer)
    print(role, "->", permitted, safe_record)

# %%
# Demonstrate feedback changing a risk score.
if findings:
    finding = findings[0]
    before = {"transaction_id": finding["transaction_id"], "risk_score": finding["risk_score"], "risk_level": finding["risk_level"]}
    submit_feedback(db, None, finding["transaction_id"], "FALSE POSITIVE", "Analyst review", "analyst")
    after = adjusted_finding(finding, db)
    print("Before feedback:", before)
    print("After feedback:", {"transaction_id": after["transaction_id"], "risk_score": after["risk_score"], "risk_level": after["risk_level"]})

# %%
# Run the real evaluation suite and print its PASS/FAIL output.
evaluation = subprocess.run([sys.executable, str(ROOT / "evaluation" / "evaluate.py")], text=True, capture_output=True, check=False)
print(evaluation.stdout)
if evaluation.returncode != 0:
    print(evaluation.stderr, file=sys.stderr)
