import json
import time
import dag_cbor
import base64

from cid import make_cid

from nacl.encoding import URLSafeBase64Encoder
from multiformats import multihash
from multibase import encode

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
    return bytes(s, 'utf-8')


def create_collection_query_message(private_key, did_public_key):
    descriptor = {
        "target": did_public_key,
        "method": "CollectionsQuery",
        "dateCreated": round(time.time() * 1000),
        "filter": {
            "schema": "https://somehost.com/CredentialManifest",
        },
    }

    authorization = sign_as_authorization(descriptor, private_key, did_public_key)
    message = {"descriptor": descriptor, "authorization": authorization}

    return message

def sign_as_authorization(descriptor, private_key, did_public_key):
    descriptor_cid = generate_cid(descriptor)

    auth_payload = {"descriptorCid": str(descriptor_cid)}
    auth_payload_str = json.dumps(auth_payload)

    # Remove spaces for perfect matching of auth payload to js
    auth_payload_str = auth_payload_str.replace(" ", "")

    auth_payload_base64_str = b64_url_encode(auth_payload_str)

    signature = sign(auth_payload_base64_str, private_key, did_public_key)
    return signature

def generate_cid(payload):
    payload_cbor_encoded = dag_cbor.encode(payload)
    payload_hash = multihash.digest(payload_cbor_encoded, "sha2-256")
    cid = make_cid(1, "dag-cbor", payload_hash)
    return bytesToString(cid.encode("base32"))

def sign(payload_str, private_key, did_public_key):
    protected_header = {
        "alg": "EdDSA",
        "kid": did_public_key + "#" + did_public_key,
    }

    protected_header_string = json.dumps(protected_header)
    protected_header_base64_url_string = b64_url_encode(protected_header_string)

    signing_input_string = (
        protected_header_base64_url_string + "." + payload_str
    )

    signing_input_bytes = stringToBytes(signing_input_string)

    signed_b64 = private_key.sign(signing_input_bytes, encoder=URLSafeBase64Encoder)

    # python leaves == even with url base64 encoders so we remove == here..
    sig = bytesToString(signed_b64.signature.rstrip(b"="))

    return_object = {
        "payload": payload_str,
        "signatures": [
            {
                "protected": protected_header_base64_url_string,
                "signature": sig,
            }
        ],
    }

    return return_object


def get_did_key_from_bytes(public_key_bytes):
    public_bytes_list = list(public_key_bytes)

    prefix = [237, 1]
    codec = bytearray(prefix)
    codec.extend(public_bytes_list)

    codec_bytes_list = list(codec)
    encoded_public_key = encode("base58btc", bytes(codec_bytes_list))

    did_public_key = "did:key:" + str(encoded_public_key.decode())

    return did_public_key