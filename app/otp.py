import secrets
import io
from pydantic import EmailStr
import redis
import qrcode
import base64
from pyotp import TOTP
from typing import Optional

class TwoFactorAuth:
    def __init__(self, email: EmailStr, secret_key: str):
        self._email = email
        self._secret_key = secret_key
        self._totp = TOTP(self._secret_key)
        self._qr_cache: Optional[bytes] = None

    @property
    def totp(self) -> TOTP:
        return self._totp

    @property
    def secret_key(self) -> str:
        return self._secret_key

    @staticmethod
    def _generate_secret_key() -> str:
        secret_bytes = secrets.token_bytes(20)
        secret_key = base64.b32encode(secret_bytes).decode('utf-8')
        return secret_key

    @staticmethod
    def get_or_create_secret_key(email: EmailStr) -> str:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        key = r.get(email)
        if key:
            return key.__str__()
        secret_key = TwoFactorAuth._generate_secret_key()
        r.set(email, secret_key)
        return secret_key

    def _create_qr_code(self) -> bytes:
        uri = self.totp.provisioning_uri(
            name=self._email,
            issuer_name='2FA',
        )
        img = qrcode.make(uri)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        return img_byte_array.getvalue()

    @property
    def qr_code(self) -> bytes:
        if self._qr_cache is None:
            self._qr_cache = self._create_qr_code()
        return self._qr_cache

    def verify_totp_code(self, totp_code: str) -> bool:
        return self.totp.verify(totp_code)
