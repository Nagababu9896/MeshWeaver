# MeshWeaver


import hashlib
import hmac
import json
from typing import Dict, Any


class MessageSecurity:
    """
    Provides HMAC-SHA256 authentication for MeshWeaver messages.
    """

    def __init__(self, secret: str):
        if not secret:
            raise ValueError("Security secret cannot be empty")

        self.secret = secret.encode("utf-8")

    def _canonical_data(self, message: Dict[str, Any]) -> bytes:
        """
        Convert a message into a consistent byte representation.
        """

        return json.dumps(
            message,
            sort_keys=True,
            separators=(",", ":"),
            default=str
        ).encode("utf-8")

    def sign(self, message: Dict[str, Any]) -> str:
        """
        Generate an HMAC-SHA256 signature.
        """

        data = self._canonical_data(message)

        return hmac.new(
            self.secret,
            data,
            hashlib.sha256
        ).hexdigest()

    def verify(
        self,
        message: Dict[str, Any],
        signature: str
    ) -> bool:
        """
        Verify a message signature.
        """

        if not signature:
            return False

        expected_signature = self.sign(message)

        return hmac.compare_digest(
            expected_signature,
            signature
        )

    def secure_message(
        self,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add an HMAC signature to a message.
        """

        secured = dict(message)

        secured["signature"] = self.sign(
            message
        )

        return secured

    def verify_message(
        self,
        message: Dict[str, Any]
    ) -> bool:
        """
        Verify a secured message.
        """

        signature = message.get("signature")

        if not signature:
            return False

        unsigned_message = dict(message)

        del unsigned_message["signature"]

        return self.verify(
            unsigned_message,
            signature
        )
    