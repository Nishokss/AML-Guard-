import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from config.settings import DB_PATH


def connect(path: str | Path = DB_PATH):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection

def init_db(path: str | Path = DB_PATH):
    connection = connect(path)
    schema = (Path(__file__).with_name("schema.sql")).read_text()
    connection.executescript(schema)
    connection.commit()
    return connection

def log_audit(username, role, action, resource, access_decision, connection=None):
    own = connection is None
    connection = connection or init_db()
    connection.execute("INSERT INTO audit_logs(username,role,action,resource,access_decision,timestamp) VALUES (?,?,?,?,?,?)", (username, role, action, resource, access_decision, datetime.now(timezone.utc).isoformat()))
    connection.commit()
    if own: connection.close()

def rows(connection, query, params=()):
    return [dict(row) for row in connection.execute(query, params).fetchall()]

def json_reasons(reasons):
    return json.dumps(reasons, ensure_ascii=True)
