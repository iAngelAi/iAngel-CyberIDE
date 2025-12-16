"""
Pydantic models for the Metrics System.

This module defines type-safe data structures for metrics collection and persistence.
All models use Pydantic V2 for validation and serialization.

Conformité: Loi 25, PIPEDA, RGPD
- No Personal Identifiable Information (PII) is collected in metrics
- Metrics are anonymized and aggregated
- Data retention: 30 days maximum
"""

from datetime import datetime, timezone
from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class OperationType(BaseModel):
    """Valid operation types for metrics recording."""
    
    type: Literal[
        "api_request",
        "database_query",
        "file_operation",
        "computation",
        "cache_hit",
        "cache_miss",
        "external_api",
        "websocket_message",
        "background_task",
        "custom"
    ] = Field(description="Type of operation being measured")


class MetricRecord(BaseModel):
    """
    Single metric record for an operation.
    
    This model ensures data validation before metrics are queued for persistence.
    All timestamps are in UTC to ensure consistency across timezones.
    """
    
    operation_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of operation (e.g., 'api_request', 'db_query')"
    )
    
    operation_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Specific operation identifier (e.g., 'GET /api/status')"
    )
    
    duration_ms: float = Field(
        ...,
        ge=0.0,
        description="Operation duration in milliseconds"
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the operation occurred"
    )
    
    success: bool = Field(
        default=True,
        description="Whether the operation completed successfully"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Error message if operation failed"
    )
    
    metadata: Optional[Dict[str, str | int | float | bool]] = Field(
        default=None,
        description="Additional context about the operation (no PII allowed)"
    )
    
    @field_validator('timestamp')
    @classmethod
    def ensure_utc_timezone(cls, v: datetime) -> datetime:
        """
        Ensure all timestamps are in UTC timezone.
        
        If a naive datetime is provided, assume UTC.
        If a timezone-aware datetime is provided, convert to UTC.
        """
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata_no_pii(cls, v: Optional[Dict[str, str | int | float | bool]]) -> Optional[Dict[str, str | int | float | bool]]:
        """
        Validate that metadata doesn't contain PII.
        
        This is a basic check - developers must ensure no PII is logged.
        Blocked keys: email, name, username, password, token, key, secret
        """
        if v is None:
            return v
        
        forbidden_keys = {
            'email', 'name', 'username', 'password', 
            'token', 'key', 'secret', 'api_key',
            'user_id', 'client_id', 'session_id'
        }
        
        for key in v.keys():
            if key.lower() in forbidden_keys:
                raise ValueError(
                    f"Metadata key '{key}' is forbidden as it may contain PII. "
                    f"Use anonymized identifiers instead."
                )
        
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsBatch(BaseModel):
    """
    Batch of metrics for efficient disk writes.
    
    The MetricsManager accumulates records and writes them in batches
    to minimize I/O operations and improve performance.
    """
    
    records: list[MetricRecord] = Field(
        default_factory=list,
        description="List of metric records in this batch"
    )
    
    batch_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the batch was created"
    )
    
    batch_id: str = Field(
        ...,
        description="Unique identifier for this batch (format: YYYYMMDD_HHMMSS_microseconds)"
    )
    
    total_records: int = Field(
        ...,
        ge=0,
        description="Number of records in this batch"
    )
    
    @field_validator('total_records')
    @classmethod
    def validate_total_records(cls, v: int, info) -> int:
        """Ensure total_records matches actual records count."""
        # Access records from values if available
        records = info.data.get('records', [])
        if records and v != len(records):
            raise ValueError(
                f"total_records ({v}) doesn't match actual records count ({len(records)})"
            )
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsStats(BaseModel):
    """
    Statistics about the metrics system performance.
    
    Used for monitoring and observability of the MetricsManager itself.
    """
    
    total_recorded: int = Field(
        default=0,
        ge=0,
        description="Total number of metrics recorded since start"
    )
    
    total_persisted: int = Field(
        default=0,
        ge=0,
        description="Total number of metrics persisted to disk"
    )
    
    queue_size: int = Field(
        default=0,
        ge=0,
        description="Current number of metrics in the queue"
    )
    
    batches_written: int = Field(
        default=0,
        ge=0,
        description="Total number of batches written to disk"
    )
    
    last_flush_timestamp: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp of the last flush operation"
    )
    
    avg_batch_size: float = Field(
        default=0.0,
        ge=0.0,
        description="Average number of records per batch"
    )
    
    is_running: bool = Field(
        default=False,
        description="Whether the background worker is running"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
