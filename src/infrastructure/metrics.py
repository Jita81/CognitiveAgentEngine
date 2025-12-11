"""Prometheus metrics for model infrastructure monitoring."""

from prometheus_client import Counter, Gauge, Histogram, Info

# =============================================================================
# Model Request Metrics
# =============================================================================

model_requests_total = Counter(
    "cae_model_requests_total",
    "Total number of model inference requests",
    ["tier", "cognitive_tier", "status"],
)

model_requests_in_flight = Gauge(
    "cae_model_requests_in_flight",
    "Number of model requests currently in progress",
    ["tier"],
)

# =============================================================================
# Token Metrics
# =============================================================================

model_tokens_total = Counter(
    "cae_model_tokens_total",
    "Total tokens consumed by model tier and type",
    ["tier", "token_type"],  # token_type: prompt, completion
)

model_tokens_per_request = Histogram(
    "cae_model_tokens_per_request",
    "Distribution of tokens per request",
    ["tier"],
    buckets=[50, 100, 200, 500, 1000, 2000, 4000, 8000],
)

# =============================================================================
# Latency Metrics
# =============================================================================

model_latency_seconds = Histogram(
    "cae_model_latency_seconds",
    "Model inference latency in seconds",
    ["tier", "cognitive_tier"],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

model_time_to_first_token = Histogram(
    "cae_model_time_to_first_token_seconds",
    "Time to first token in seconds (when streaming)",
    ["tier"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0],
)

# =============================================================================
# Budget Metrics
# =============================================================================

budget_utilization = Gauge(
    "cae_budget_utilization",
    "Budget utilization ratio (0-1)",
    ["tier"],
)

budget_cost_usd = Gauge(
    "cae_budget_cost_usd",
    "Estimated cost in USD this hour",
    ["tier"],
)

hourly_budget_usd = Gauge(
    "cae_hourly_budget_usd",
    "Configured hourly budget in USD",
)

# =============================================================================
# Throttling Metrics
# =============================================================================

throttle_events_total = Counter(
    "cae_throttle_events_total",
    "Total throttling events by tier",
    ["tier", "reason"],  # reason: budget, health, timeout
)

tier_downgrades_total = Counter(
    "cae_tier_downgrades_total",
    "Total tier downgrades",
    ["from_tier", "to_tier", "reason"],
)

# =============================================================================
# Health Metrics
# =============================================================================

model_health_status = Gauge(
    "cae_model_health_status",
    "Model endpoint health status (1=healthy, 0=unhealthy)",
    ["tier"],
)

model_health_check_duration = Histogram(
    "cae_model_health_check_duration_seconds",
    "Duration of health check requests",
    ["tier"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
)

# =============================================================================
# Error Metrics
# =============================================================================

model_errors_total = Counter(
    "cae_model_errors_total",
    "Total model errors by type",
    ["tier", "error_type"],  # error_type: timeout, connection, http_error, other
)

# =============================================================================
# Info Metrics
# =============================================================================

model_info = Info(
    "cae_model",
    "Model configuration information",
)


# =============================================================================
# Helper Functions
# =============================================================================


def record_request_start(tier: str, cognitive_tier: str) -> None:
    """Record the start of a model request."""
    model_requests_in_flight.labels(tier=tier).inc()


def record_request_end(
    tier: str,
    cognitive_tier: str,
    status: str,
    latency_seconds: float,
    prompt_tokens: int,
    completion_tokens: int,
) -> None:
    """Record the completion of a model request.

    Args:
        tier: Model tier (small, medium, large)
        cognitive_tier: Cognitive tier (reflex, reactive, etc.)
        status: Request status (success, error, timeout)
        latency_seconds: Total request latency
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
    """
    # Update in-flight counter
    model_requests_in_flight.labels(tier=tier).dec()

    # Record request
    model_requests_total.labels(
        tier=tier, cognitive_tier=cognitive_tier, status=status
    ).inc()

    # Record latency
    model_latency_seconds.labels(tier=tier, cognitive_tier=cognitive_tier).observe(
        latency_seconds
    )

    # Record tokens
    if status == "success":
        total_tokens = prompt_tokens + completion_tokens
        model_tokens_total.labels(tier=tier, token_type="prompt").inc(prompt_tokens)
        model_tokens_total.labels(tier=tier, token_type="completion").inc(
            completion_tokens
        )
        model_tokens_per_request.labels(tier=tier).observe(total_tokens)


def record_throttle_event(tier: str, reason: str) -> None:
    """Record a throttling event.

    Args:
        tier: Model tier being throttled
        reason: Reason for throttling (budget, health, timeout)
    """
    throttle_events_total.labels(tier=tier, reason=reason).inc()


def record_tier_downgrade(from_tier: str, to_tier: str, reason: str) -> None:
    """Record a tier downgrade.

    Args:
        from_tier: Original tier
        to_tier: Downgraded tier
        reason: Reason for downgrade
    """
    tier_downgrades_total.labels(
        from_tier=from_tier, to_tier=to_tier, reason=reason
    ).inc()


def record_error(tier: str, error_type: str) -> None:
    """Record a model error.

    Args:
        tier: Model tier where error occurred
        error_type: Type of error (timeout, connection, http_error, other)
    """
    model_errors_total.labels(tier=tier, error_type=error_type).inc()


def update_health_status(tier: str, is_healthy: bool) -> None:
    """Update health status metric.

    Args:
        tier: Model tier
        is_healthy: Whether the tier is healthy
    """
    model_health_status.labels(tier=tier).set(1 if is_healthy else 0)


def update_budget_metrics(
    tier: str,
    utilization: float,
    cost_usd: float,
    total_budget_usd: float,
) -> None:
    """Update budget-related metrics.

    Args:
        tier: Model tier
        utilization: Budget utilization ratio (0-1)
        cost_usd: Current cost in USD
        total_budget_usd: Total hourly budget
    """
    budget_utilization.labels(tier=tier).set(utilization)
    budget_cost_usd.labels(tier=tier).set(cost_usd)
    hourly_budget_usd.set(total_budget_usd)


def set_model_info(models: dict) -> None:
    """Set model configuration info.

    Args:
        models: Dictionary of model configurations
    """
    model_info.info(models)

