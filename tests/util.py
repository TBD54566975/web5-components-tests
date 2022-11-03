import json
import time
import cbor2
import base64
import hashlib

from cid import make_cid

from multihash import multihash
from nacl.encoding import URLSafeBase64Encoder
from multibase import encode


def b64_encode(s):
    return base64.urlsafe_b64encode(s.encode()).decode()


def b64decode(s):
    return base64.urlsafe_b64decode(s).decode()


def bytesToString(b):
    return b.decode("utf-8")


def stringToBytes(s):
    return bytes(s, "utf-8")


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
    auth_payload_base64_bytes = stringToBytes(b64_encode(auth_payload_str))

    signature = sign(auth_payload_base64_bytes, private_key, did_public_key)
    return signature


def generate_cid(payload):
    ob_cbor = cbor2.dumps(payload)
    ob_cbor_hash = hashlib.sha256(ob_cbor).digest()
    mh = multihash.encode(digest=ob_cbor_hash, code=18)

    cid = make_cid(1, "dag-pb", mh)
    return bytesToString(cid.encode("base32"))


def sign(payload_bytes, private_key, did_public_key):
    protected_header = {
        "alg": "EdDSA",
        "kid": did_public_key + "#" + did_public_key,
    }

    protected_header_string = json.dumps(protected_header)
    protected_header_base64_url_string = b64_encode(protected_header_string)

    signing_input_string = (
        protected_header_base64_url_string + "." + bytesToString(payload_bytes)
    )

    signing_input_bytes = stringToBytes(signing_input_string)

    signed_b64 = private_key.sign(signing_input_bytes, encoder=URLSafeBase64Encoder)

    return_object = {
        "payload": bytesToString(payload_bytes),
        "signatures": [
            {
                "protected": protected_header_base64_url_string,
                "signature": bytesToString(signed_b64.signature),
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
