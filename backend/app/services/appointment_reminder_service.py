"""In-app reminder delivery for scheduled advisor consultations."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.advisor import AdvisorBookingReminder, AdvisorBookingRequest
from app.models.enums import NotificationType
from app.models.notification import Notification


def send_due_appointment_reminders(session: Session) -> int:
    """Create one 24-hour and one 1-hour reminder per accepted appointment."""
    now = datetime.now(UTC).replace(tzinfo=None)
    bookings = session.scalars(select(AdvisorBookingRequest).where(AdvisorBookingRequest.status == "accepted", AdvisorBookingRequest.scheduled_at.is_not(None))).all()
    created = 0
    for booking in bookings:
        assert booking.scheduled_at is not None
        remaining = booking.scheduled_at - now
        for kind, threshold, label in (("24h", timedelta(hours=24), "24 hours"), ("1h", timedelta(hours=1), "1 hour")):
            if not timedelta(0) <= remaining <= threshold:
                continue
            exists = session.scalar(select(AdvisorBookingReminder).where(AdvisorBookingReminder.booking_request_id == booking.id, AdvisorBookingReminder.reminder_kind == kind))
            if exists:
                continue
            time_text = booking.scheduled_at.strftime("%d %b %Y, %I:%M %p")
            for user_id in (booking.founder_id, booking.advisor_id):
                session.add(Notification(user_id=user_id, notification_type=NotificationType.SYSTEM, title="Upcoming consultation reminder", body=f"Your consultation about '{booking.topic}' is in {label}: {time_text}.", payload={"booking_request_id": booking.id, "meeting_url": booking.meeting_url, "path": "/advisor-dashboard" if user_id == booking.advisor_id else "/dashboard"}))
            session.add(AdvisorBookingReminder(booking_request_id=booking.id, reminder_kind=kind))
            created += 1
    if created:
        session.commit()
    return created
