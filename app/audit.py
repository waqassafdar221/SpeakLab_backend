from sqlalchemy.orm import Session
from .models import AuditLog, User


def log_action(
    db: Session,
    actor: User,
    action: str,
    *,
    target_type: str | None = None,
    target_id: int | None = None,
    target_username: str | None = None,
    details: str | None = None,
) -> None:
    """Record an admin/vendor action. Commits on its own so a failure here
    never rolls back the action it's logging."""
    entry = AuditLog(
        actor_id=actor.id,
        actor_username=actor.username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_username=target_username,
        details=details,
    )
    db.add(entry)
    db.commit()
