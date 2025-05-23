"""SMS notification service with mock and Twilio providers."""

import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, Union

from app.core.config import settings


class SMSProvider(ABC):
    """Abstract base class for SMS providers."""

    @abstractmethod
    def send_sms(self, to: str, body: str) -> dict[str, Any]:
        """Send an SMS message."""
        pass


class MockSMSProvider(SMSProvider):
    """Mock SMS provider for development and testing."""

    def __init__(self):
        self._sent_messages: list[dict[str, Any]] = []

    def send_sms(self, to: str, body: str) -> dict[str, Any]:
        """Simulate sending an SMS."""
        message = {
            "success": True,
            "message_id": f"mock_{uuid.uuid4().hex[:8]}",
            "to": to,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
            "provider": "mock",
        }
        self._sent_messages.append(message)

        # Log the message in development
        if settings.debug:
            print("\n📱 MOCK SMS SENT:")
            print(f"To: {to}")
            print(f"Message: {body}")
            print(f"ID: {message['message_id']}\n")

        return message

    def get_sent_messages(self) -> list[dict[str, Any]]:
        """Get all sent messages (for testing)."""
        return self._sent_messages.copy()

    def clear_messages(self):
        """Clear sent messages (for testing)."""
        self._sent_messages.clear()


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider for production."""

    def __init__(self):
        if not all(
            [
                settings.twilio_account_sid,
                settings.twilio_auth_token,
                settings.twilio_phone_number,
            ]
        ):
            raise ValueError("Twilio credentials not configured")

        # Import only when needed
        from twilio.rest import Client

        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = settings.twilio_phone_number

    def send_sms(self, to: str, body: str) -> dict[str, Any]:
        """Send SMS via Twilio."""
        try:
            message = self.client.messages.create(
                body=body, from_=self.from_number, to=to
            )
            return {
                "success": True,
                "message_id": message.sid,
                "to": to,
                "body": body,
                "provider": "twilio",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "to": to,
                "body": body,
                "provider": "twilio",
            }


class SMSService:
    """Main SMS service that uses different providers."""

    def __init__(self, provider: Optional[Union[str, SMSProvider]] = None):
        self.provider: SMSProvider
        if provider is None:
            # Default to mock in development, Twilio in production
            if settings.environment == "development":
                self.provider = MockSMSProvider()
            else:
                self.provider = TwilioSMSProvider()
        elif isinstance(provider, str):
            if provider == "mock":
                self.provider = MockSMSProvider()
            elif provider == "twilio":
                self.provider = TwilioSMSProvider()
            else:
                raise ValueError(f"Unknown provider: {provider}")
        else:
            self.provider = provider

    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format."""
        # Simple validation - starts with + and has 10-15 digits
        pattern = r"^\+\d{10,15}$"
        return bool(re.match(pattern, phone_number))

    def send_queue_joined_notification(
        self,
        phone_number: str,
        queue_name: str,
        position: int,
        estimated_wait_minutes: int,
    ) -> dict[str, Any]:
        """Send notification when customer joins queue."""
        if not self._validate_phone_number(phone_number):
            return {"success": False, "error": "Invalid phone number format"}

        body = (
            f"Welcome to {queue_name}! You are in position {position}. "
            f"Estimated wait time: {estimated_wait_minutes} minutes. "
            f"We'll notify you when it's your turn."
        )
        return self.provider.send_sms(phone_number, body)

    def send_customer_called_notification(
        self, phone_number: str, queue_name: str
    ) -> dict[str, Any]:
        """Send notification when customer is called."""
        if not self._validate_phone_number(phone_number):
            return {"success": False, "error": "Invalid phone number format"}

        body = f"🔔 Your turn is ready at {queue_name}! Please come to the counter now."
        return self.provider.send_sms(phone_number, body)

    def send_position_update_notification(
        self,
        phone_number: str,
        queue_name: str,
        new_position: int,
        estimated_wait_minutes: int,
    ) -> dict[str, Any]:
        """Send notification when customer's position changes."""
        if not self._validate_phone_number(phone_number):
            return {"success": False, "error": "Invalid phone number format"}

        body = (
            f"Update from {queue_name}: You are now in position {new_position}. "
            f"Estimated wait time: {estimated_wait_minutes} minutes."
        )
        return self.provider.send_sms(phone_number, body)


# Global instance
sms_service = SMSService()
