from pathlib import Path
import pandas as pd

REQUIRED = {"transaction_id", "customer_id", "amount", "country", "date", "sender_name", "receiver_name", "description"}

def load_transactions(path, connection):
    path = Path(path)
    frame = pd.read_excel(path) if path.suffix.lower() in {".xls", ".xlsx"} else pd.read_csv(path)
    missing = REQUIRED - set(frame.columns)
    if missing: raise ValueError(f"Missing transaction columns: {', '.join(sorted(missing))}")
    frame = frame.fillna("")
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0)
    columns = list(REQUIRED | {"risk_score"})
    if "risk_score" not in frame: frame["risk_score"] = 0
    frame = frame[columns]
    frame.to_sql("transactions", connection, if_exists="replace", index=False)
    connection.commit()
    return len(frame)
