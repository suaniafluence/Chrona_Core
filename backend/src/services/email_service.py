"""Email service for sending OTP codes and notifications."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.config.email import EmailProvider, EmailSettings, get_email_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via various providers."""

    def __init__(self, settings: Optional[EmailSettings] = None):
        """Initialize email service.

        Args:
            settings: Email settings (defaults to global settings)
        """
        self.settings = settings or get_email_settings()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send email via configured provider.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        # Test mode: log email but don't send
        if self.settings.EMAIL_TEST_MODE:
            logger.info(
                f"[TEST MODE] Email to {to_email}\n"
                f"Subject: {subject}\n"
                f"Body: {text_body or html_body}"
            )
            return True

        # Override recipient in test mode
        recipient = (
            self.settings.EMAIL_TEST_RECIPIENT
            if self.settings.EMAIL_TEST_RECIPIENT
            else to_email
        )

        try:
            if self.settings.EMAIL_PROVIDER == EmailProvider.SMTP:
                return await self._send_via_smtp(
                    recipient, subject, html_body, text_body
                )
            elif self.settings.EMAIL_PROVIDER == EmailProvider.SENDGRID:
                return await self._send_via_sendgrid(
                    recipient, subject, html_body, text_body
                )
            elif self.settings.EMAIL_PROVIDER == EmailProvider.CONSOLE:
                return self._send_via_console(recipient, subject, html_body, text_body)
            else:
                logger.error(f"Unknown email provider: {self.settings.EMAIL_PROVIDER}")
                return False
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body

        Returns:
            True if sent successfully
        """
        if not self.settings.SMTP_USERNAME or not self.settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = (
                f"{self.settings.EMAIL_FROM_NAME} <{self.settings.EMAIL_FROM_ADDRESS}>"
            )
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add plain text version
            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))

            # Add HTML version
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Connect to SMTP server
            if self.settings.SMTP_USE_TLS:
                server = smtplib.SMTP(self.settings.SMTP_HOST, self.settings.SMTP_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(
                    self.settings.SMTP_HOST, self.settings.SMTP_PORT
                )

            # Login and send
            server.login(self.settings.SMTP_USERNAME, self.settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email} via SMTP")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
            return False

    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send email via SendGrid API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body

        Returns:
            True if sent successfully
        """
        if not self.settings.SENDGRID_API_KEY:
            logger.error("SendGrid API key not configured")
            return False

        try:
            # Import SendGrid (optional dependency)
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Content, Email, Mail, To

            # Create message
            from_email = Email(
                self.settings.EMAIL_FROM_ADDRESS, self.settings.EMAIL_FROM_NAME
            )
            to_email_obj = To(to_email)
            content = Content("text/html", html_body)

            mail = Mail(from_email, to_email_obj, subject, content)

            # Add plain text version if provided
            if text_body:
                mail.add_content(Content("text/plain", text_body))

            # Send via SendGrid API
            sg = SendGridAPIClient(self.settings.SENDGRID_API_KEY)
            response = sg.send(mail)

            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email} via SendGrid")
                return True
            else:
                logger.error(
                    f"SendGrid API error: {response.status_code} - {response.body}"
                )
                return False

        except ImportError:
            logger.error(
                "SendGrid library not installed. Install with: pip install sendgrid"
            )
            return False
        except Exception as e:
            logger.error(f"SendGrid error sending email to {to_email}: {str(e)}")
            return False

    def _send_via_console(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Print email to console (development mode).

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body

        Returns:
            Always True
        """
        print("\n" + "=" * 80)
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] From: {self.settings.EMAIL_FROM_ADDRESS}")
        print(f"[EMAIL] Subject: {subject}")
        print("=" * 80)
        print(text_body or html_body)
        print("=" * 80 + "\n")

        logger.info(f"Email printed to console for {to_email}")
        return True

    async def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        """Send OTP verification code via email.

        Args:
            to_email: Recipient email address
            otp_code: OTP code to send

        Returns:
            True if email sent successfully
        """
        subject = self.settings.OTP_SUBJECT

        # Generate HTML body
        html_body = self._generate_otp_html(otp_code)

        # Generate plain text body
        text_body = self._generate_otp_text(otp_code)

        return await self.send_email(to_email, subject, html_body, text_body)

    def _generate_otp_html(self, otp_code: str) -> str:
        """Generate HTML email template for OTP.

        Args:
            otp_code: OTP code to include

        Returns:
            HTML email body
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code de vérification Chrona</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">  # noqa: E501
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">  # noqa: E501
        <h1 style="color: white; margin: 0; font-size: 28px;">Chrona</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">Système de pointage sécurisé</p>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Code de vérification</h2>

        <p>Bonjour,</p>

        <p>Vous avez demandé un code de vérification pour finaliser votre inscription sur Chrona.</p>  # noqa: E501

        <div style="background: white; border: 2px solid #667eea; border-radius: 8px; padding: 20px; margin: 30px 0; text-align: center;">  # noqa: E501
            <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">Votre code de vérification :</p>  # noqa: E501
            <p style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 8px; margin: 0; font-family: 'Courier New', monospace;">  # noqa: E501
                {otp_code}
            </p>
        </div>

        <p style="color: #666; font-size: 14px;">
            <strong>⏱️ Ce code expire dans {self.settings.OTP_EXPIRY_MINUTES} minutes.</strong>  # noqa: E501
        </p>

        <p style="color: #666; font-size: 14px;">
            Si vous n'avez pas demandé ce code, vous pouvez ignorer cet email en toute sécurité.  # noqa: E501
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

        <p style="color: #999; font-size: 12px; text-align: center;">
            Cet email a été envoyé automatiquement par Chrona.<br>
            Veuillez ne pas répondre à ce message.
        </p>
    </div>
</body>
</html>
"""

    def _generate_otp_text(self, otp_code: str) -> str:
        """Generate plain text email template for OTP.

        Args:
            otp_code: OTP code to include

        Returns:
            Plain text email body
        """
        return f"""
Chrona - Code de vérification
==============================

Bonjour,

Vous avez demandé un code de vérification pour finaliser votre inscription sur Chrona.

Votre code de vérification : {otp_code}

Ce code expire dans {self.settings.OTP_EXPIRY_MINUTES} minutes.

Si vous n'avez pas demandé ce code, vous pouvez ignorer cet email en toute sécurité.

---
Cet email a été envoyé automatiquement par Chrona.
Veuillez ne pas répondre à ce message.
"""


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton instance.

    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
