from security.rbac import protect_customer_record

def test_role_specific_customer_access():
    record = {"customer_id":"C001", "name":"John Smith", "phone":"9876543210", "address":"Secret"}
    assert protect_customer_record("ADMIN", record)[1]["name"] == "John Smith"
    assert "John Smith" not in protect_customer_record("AML_ANALYST", record)[1]["name"]
    assert protect_customer_record("EXTERNAL_AUDITOR", record)[0] is False

def test_relationship_manager_is_limited_to_portfolio():
    in_scope = {"customer_id": "C001", "name": "John Smith"}
    outside_scope = {"customer_id": "C011", "name": "Priya Shah"}
    assert protect_customer_record("RELATIONSHIP_MANAGER", in_scope)[0] is True
    assert protect_customer_record("RELATIONSHIP_MANAGER", in_scope)[1]["name"] != "John Smith"
    assert protect_customer_record("RELATIONSHIP_MANAGER", outside_scope) == (False, None)
