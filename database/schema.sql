CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT);
CREATE TABLE IF NOT EXISTS transactions (transaction_id TEXT PRIMARY KEY, customer_id TEXT, amount REAL, country TEXT, date TEXT, sender_name TEXT, receiver_name TEXT, description TEXT, risk_score REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS sanctions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, entity_type TEXT, country TEXT, sanctions_program TEXT, normalized_name TEXT);
CREATE TABLE IF NOT EXISTS alerts (alert_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id TEXT, risk_level TEXT, reasons TEXT, status TEXT DEFAULT 'OPEN', created_at TEXT);
CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, alert_id INTEGER, transaction_id TEXT, decision TEXT, comment TEXT, user TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, action TEXT, resource TEXT, access_decision TEXT, timestamp TEXT);
