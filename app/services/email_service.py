import smtplib
from email.message import EmailMessage

from fastapi import HTTPException

from app.core.config import settings


def _build_message(to_email: str, subject: str, body: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content(body)
    return message


def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.EMAIL_ENABLED:
        return

    if settings.EMAIL_BACKEND == "console":
        print(
            "\n".join(
                [
                    "[EMAIL][console]",
                    f"To: {to_email}",
                    f"Subject: {subject}",
                    body,
                ]
            )
        )
        return

    if not settings.SMTP_HOST:
        raise HTTPException(status_code=500, detail="SMTP_HOST is not configured.")

    message = _build_message(to_email, subject, body)

    try:
        if settings.SMTP_USE_SSL:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
            return

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except smtplib.SMTPException as exc:
        raise HTTPException(status_code=502, detail="Failed to send email.") from exc


def send_verification_email(to_email: str, verification_code: str) -> None:
    send_email(
        to_email=to_email,
        subject="Verify your Cortts account",
        body=(
            "Welcome to Cortts.\n\n"
            f"Use this verification code to activate your account: {verification_code}\n\n"
            "If you did not create this account, you can ignore this email."
        ),
    )


def send_password_reset_email(to_email: str, verification_code: str) -> None:
    send_email(
        to_email=to_email,
        subject="Your Cortts password reset code",
        body=(
            "We received a request to reset your Cortts password.\n\n"
            f"Use this code to continue: {verification_code}\n\n"
            "If you did not request a password reset, you can ignore this email."
        ),
    )
