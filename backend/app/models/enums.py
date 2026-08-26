"""String enums persisted by the application models."""

from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    FOUNDER = "founder"
    ADMIN = "admin"
    LEGAL_ADVISOR = "legal_advisor"
    BUSINESS_MENTOR = "business_mentor"
    JOB_APPLICANT = "job_applicant"
    INVESTOR = "investor"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class DevelopmentStage(StrEnum):
    IDEA = "idea"
    RESEARCH = "research"
    MVP = "mvp"
    PROTOTYPE = "prototype"
    TESTING = "testing"
    LAUNCHED = "launched"
    GROWTH = "growth"


class EvaluationStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class FeedbackStatus(StrEnum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"


class NotificationType(StrEnum):
    EVALUATION_READY = "evaluation_ready"
    REPORT_READY = "report_ready"
    SYSTEM = "system"
    ACCOUNT = "account"


class SecurityTokenType(StrEnum):
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
