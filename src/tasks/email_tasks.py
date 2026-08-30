import logging
import time

from src.tasks.worker import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name="send_booking_confirmation_email", bind=True, max_retries=3)
def send_booking_confirmation_email(
        self,
        email: str,
        booking_id: int,
        event_title: str,
        tickets_count: int,
        total_price: int
):
    try:
        logger.info(f"Start ticked sending to email {email} for booking{booking_id}")
        time.sleep(2)
        logger.info(f"Ticket for event '{event_title}' ({tickets_count} pcs., sum: {total_price}) was sent on {email}")
    except Exception as exc:
        logger.error(f"Sending error: {exc}")
        raise self.retry(exc=exc, countdown=10)