import base64
import uuid
from jose import jwt


def create_jwt(json_data, secret):
    token = jwt.encode(json_data, secret, algorithm="HS256")
    return token


def b64_url_encode(value: str) -> str:
    encoded = base64.urlsafe_b64encode(str.encode(value))
    result = encoded.rstrip(b"=")
    return result.decode()


def b64_url_encode_bytes(value: bytes) -> str:
    encoded = base64.urlsafe_b64encode(value)
    result = encoded.rstrip(b"=")
    return result.decode()


def bytesToString(b):
    return b.decode("utf-8")


def stringToBytes(s):
    return bytes(s, "utf-8")


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
