import json
from typing import Dict, Any

# In a real application, this would write to a database or a dedicated log file.
# For this mock implementation, we will print to the console and store in a simple list.
_audit_log = []

def log_state_mutation(entity_type: str, action: str, data: Dict[str, Any]):
    """
    Logs a state mutation event for auditing purposes.
    This function is a pure function that records the event.
    """
    log_entry = {
        "timestamp": "2023-10-27T10:00:00Z", # Mock timestamp
        "entity_type": entity_type,
        "action": action,
        "data": data
    }
    _audit_log.append(log_entry)
    print(f"AUDIT LOGGED: {entity_type} {action} - {json.dumps(data, indent=2)}")

def get_audit_log() -> list:
    """
    Retrieves the entire audit log.
    """
    return _audit_log