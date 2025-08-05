from rasa.core.channels.twilio import TwilioInput
from rasa.core.channels.channel import UserMessage
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Any, Dict, Optional
from twilio.twiml.messaging_response import MessagingResponse


class FixedTwilioInput(TwilioInput):
    @classmethod
    def name(cls) -> Text:
        return "fixed_twilio"

    def blueprint(self, on_new_message):
        twilio_webhook = Blueprint("twilio_webhook", __name__)

        @twilio_webhook.route("/webhook", methods=["POST"])
        async def message(request: Request) -> Any:
            sender_id = request.form.get("From")
            if not sender_id.startswith("whatsapp:"):
                sender_id = "whatsapp:" + sender_id

            text = request.form.get("Body")
            input_channel = self.name()
            metadata = self.get_metadata(request)

            collector = self.get_output_channel()

            user_msg = UserMessage(
                text,
                collector,
                sender_id,
                input_channel=input_channel,
                metadata=metadata,
            )

            await on_new_message(user_msg)

            return response.text("", status=204)

        return twilio_webhook
