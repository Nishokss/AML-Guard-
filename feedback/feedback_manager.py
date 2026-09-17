from datetime import datetime, timezone

def submit_feedback(connection, alert_id, transaction_id, decision, comment, user):
    connection.execute("INSERT INTO feedback(alert_id,transaction_id,decision,comment,user,created_at) VALUES (?,?,?,?,?,?)", (alert_id, transaction_id, decision, comment, user, datetime.now(timezone.utc).isoformat()))
    connection.commit()

def feedback_adjustment(connection, transaction_id):
    rows = connection.execute("SELECT decision FROM feedback WHERE transaction_id = ?", (transaction_id,)).fetchall()
    return -20 * sum(row["decision"] == "FALSE POSITIVE" for row in rows) + 10 * sum(row["decision"] == "TRUE HIT" for row in rows)

def adjusted_finding(finding, connection):
    score = max(0, min(100, int(finding["risk_score"]) + feedback_adjustment(connection, finding["transaction_id"])))
    return {**finding, "risk_score": score, "risk_level": "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"}
