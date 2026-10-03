import logging

logger = logging.getLogger(__name__)


def send_sos_sms(alert, phone_numbers):
    """Log the intended SOS recipients until an SMS provider is configured."""
    if not phone_numbers:
        logger.warning("SOS alert %s has no available guide phone numbers.", alert.pk)
        return "no_recipients"

    logger.warning(
        "SMS provider not configured. SOS alert %s would notify %d guide(s) at %s "
        "with coordinates %s,%s.",
        alert.pk,
        len(phone_numbers),
        ", ".join(phone_numbers),
        alert.latitude,
        alert.longitude,
    )
    return "provider_not_configured"
