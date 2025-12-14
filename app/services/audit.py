import json
from app.extensions import db
from app.models import AuditLog

def log_action(user_id, action, entity_type=None, entity_id=None, before=None, after=None):
    """
    Logs an action to the audit log table.
    before and after should be dictionaries or None.
    """
    before_json = json.dumps(before, default=str) if before else None
    after_json = json.dumps(after, default=str) if after else None

    log_entry = AuditLog(
        actor_user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=before_json,
        after_json=after_json
    )
    db.session.add(log_entry)
    # Note: Calling function is expected to commit the session usually, 
    # but we can commit here to ensure log is saved even if main transaction fails? 
    # Standard practice: part of same transaction.
