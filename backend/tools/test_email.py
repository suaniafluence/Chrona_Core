"""Test script for email sending functionality.

IMPORTANT: This is an INTERACTIVE test tool for manual testing only.
It is NOT intended to be run by pytest. Run it directly with:
    python backend/tools/test_email.py
"""

import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.services.email_service import get_email_service


async def test_otp_email():
    """Test OTP email sending."""
    print("=" * 80)
    print("Testing OTP Email Sending")
    print("=" * 80)

    email_service = get_email_service()

    # Display current configuration
    print(f"\nConfiguration:")
    print(f"  Provider: {email_service.settings.EMAIL_PROVIDER}")
    print(f"  From: {email_service.settings.EMAIL_FROM_ADDRESS}")
    print(f"  Test Mode: {email_service.settings.EMAIL_TEST_MODE}")

    if email_service.settings.EMAIL_PROVIDER.value == "smtp":
        print(f"  SMTP Host: {email_service.settings.SMTP_HOST}")
        print(f"  SMTP Port: {email_service.settings.SMTP_PORT}")
        print(
            f"  SMTP Username: {email_service.settings.SMTP_USERNAME or 'Not configured'}"
        )

    # Test email
    test_email = input("\nEnter test email address: ").strip()
    if not test_email:
        test_email = "test@example.com"
        print(f"Using default: {test_email}")

    test_otp = "123456"

    print(f"\nSending OTP email to {test_email}...")
    print(f"OTP Code: {test_otp}")

    try:
        success = await email_service.send_otp_email(test_email, test_otp)

        if success:
            print("\n✅ Email sent successfully!")
            if email_service.settings.EMAIL_PROVIDER.value == "console":
                print("\n(Email was printed to console above)")
            else:
                print(f"\nCheck the inbox for {test_email}")
        else:
            print("\n❌ Failed to send email")
            print("Check the logs above for error details")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)


async def test_custom_email():
    """Test custom email sending."""
    print("=" * 80)
    print("Testing Custom Email Sending")
    print("=" * 80)

    email_service = get_email_service()

    test_email = input("\nEnter test email address: ").strip()
    if not test_email:
        test_email = "test@example.com"

    subject = "Test Email from Chrona"
    html_body = """
    <h1>Test Email</h1>
    <p>This is a test email from Chrona backend.</p>
    <p>If you received this, email sending is working correctly!</p>
    """
    text_body = "Test Email\n\nThis is a test email from Chrona backend."

    print(f"\nSending test email to {test_email}...")

    try:
        success = await email_service.send_email(
            test_email, subject, html_body, text_body
        )

        if success:
            print("\n✅ Email sent successfully!")
        else:
            print("\n❌ Failed to send email")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    print("\n" + "=" * 80)


async def main():
    """Main test menu."""
    while True:
        print("\n" + "=" * 80)
        print("Email Service Test Menu")
        print("=" * 80)
        print("\n1. Test OTP Email")
        print("2. Test Custom Email")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            await test_otp_email()
        elif choice == "2":
            await test_custom_email()
        elif choice == "3":
            print("\nExiting...")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-3.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
