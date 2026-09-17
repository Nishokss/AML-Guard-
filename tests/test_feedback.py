from database.database import init_db
from feedback.feedback_manager import submit_feedback, adjusted_finding

def test_feedback_changes_score(tmp_path):
    db = init_db(tmp_path / "test.db"); finding = {"transaction_id":"T1", "risk_score":80, "risk_level":"HIGH"}
    submit_feedback(db, 1, "T1", "FALSE POSITIVE", "reviewed", "analyst")
    assert adjusted_finding(finding, db)["risk_score"] == 60
