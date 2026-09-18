from pathlib import Path
import pandas as pd
from utils.helpers import normalize_name

REQUIRED = {"name", "entity_type", "country", "sanctions_program"}

def load_sanctions(path, connection):
    frame = pd.read_excel(path) if Path(path).suffix.lower() in {".xls", ".xlsx"} else pd.read_csv(path)
    frame.columns = [str(column).replace("\ufeff", "").strip().lower().replace(" ", "_") for column in frame.columns]
    missing = REQUIRED - set(frame.columns)
    if missing: raise ValueError(f"Missing sanctions columns: {', '.join(sorted(missing))}")
    frame = frame.fillna(""); frame["normalized_name"] = frame["name"].map(normalize_name)
    frame.to_sql("sanctions", connection, if_exists="replace", index=False)
    connection.commit(); return len(frame)

def match_sanctions(name, connection):
    normalized = normalize_name(name)
    exact = connection.execute("SELECT * FROM sanctions WHERE normalized_name = ?", (normalized,)).fetchall()
    if exact: return {"status": "Exact match", "matches": [dict(row) for row in exact]}
    tokens = set(normalized.split())
    matches = []
    for row in connection.execute("SELECT * FROM sanctions").fetchall():
        candidate = set(row["normalized_name"].split())
        if tokens and candidate and len(tokens & candidate) / max(len(tokens), len(candidate)) >= 0.5:
            matches.append(dict(row))
    return {"status": "Possible match" if matches else "No match", "matches": matches}
