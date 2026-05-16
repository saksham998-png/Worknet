from flask import request
from models import db, AuditLog


def log_audit(user, action, details, workspace=None):
    entry = AuditLog(
        user=user,
        action=action,
        details=details,
        workspace=workspace or user.workspace,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    db.session.commit()
    return entry
