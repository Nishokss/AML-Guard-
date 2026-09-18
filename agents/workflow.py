from agents.screening_agent import ScreeningAgent
from agents.investigation_agent import InvestigationAgent
from database.database import log_audit
from config.roles import scoped_customers
from security.rbac import access, customer_in_scope

class AMLWorkflow:
    def __init__(self, connection): self.connection = connection
    def run(self, question, username, role, use_llm=True):
        allowed = [permission for permission in ("transactions", "alerts", "regulations", "sanctions", "customer_pii", "masked_customer") if access(role, permission)]
        log_audit(username, role, "access_check", "aml_workflow", "ALLOWED" if "transactions" in allowed or "regulations" in allowed else "DENIED", self.connection)
        if not allowed: return {"access_decision": "DENIED", "final_answer": "ACCESS DENIED", "workflow": []}
        screening = ScreeningAgent(self.connection).run(question, customer_ids=scoped_customers(role)) if "transactions" in allowed else []
        log_audit(username, role, "agent_execution", "screening", "ALLOWED", self.connection)
        investigation = InvestigationAgent(self.connection).run(screening, question, use_llm=use_llm)
        log_audit(username, role, "agent_handoff", "screening_to_investigation", "ALLOWED", self.connection)
        log_audit(username, role, "final_response", "aml_workflow", "ALLOWED", self.connection)
        return {"access_decision": "ALLOWED", "allowed_data": allowed, "screening_findings": screening, "verification": investigation["verified_findings"], "final_answer": investigation["final_answer"], "workflow": ["RBAC check completed", "Agent 1: Screening completed", "Agent 2: Verification started", "Agent 2: Verification completed"]}
