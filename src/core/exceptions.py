"""Custom exceptions for the Cognitive Agent Engine."""

from typing import Any, Optional


class CAEException(Exception):
    """Base exception for all CAE errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AgentNotFoundError(CAEException):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent with ID {agent_id} not found",
            code="AGENT_NOT_FOUND",
            details={"agent_id": agent_id},
        )


class AgentLimitExceededError(CAEException):
    """Raised when the maximum number of active agents is exceeded."""

    def __init__(self, limit: int):
        super().__init__(
            message=f"Maximum active agents limit ({limit}) exceeded",
            code="AGENT_LIMIT_EXCEEDED",
            details={"limit": limit},
        )


class BudgetExceededError(CAEException):
    """Raised when the budget limit is exceeded."""

    def __init__(self, current: float, limit: float):
        super().__init__(
            message=f"Budget limit exceeded: ${current:.2f} / ${limit:.2f}",
            code="BUDGET_EXCEEDED",
            details={"current": current, "limit": limit},
        )


class ModelUnavailableError(CAEException):
    """Raised when a model tier is unavailable."""

    def __init__(self, tier: str):
        super().__init__(
            message=f"Model tier '{tier}' is currently unavailable",
            code="MODEL_UNAVAILABLE",
            details={"tier": tier},
        )


class ValidationError(CAEException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )


class DatabaseError(CAEException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details={"operation": operation} if operation else {},
        )

