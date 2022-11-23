import json
import time
import dag_cbor

# import util
from common.util import *

from cid import make_cid, from_bytes

from nacl.encoding import URLSafeBase64Encoder
from multiformats import multihash
from multibase import encode


def create_collection_write_message(private_key, did_public_key, data):
    encoded_data = b64_url_encode(json.dumps(data))

    encoded_data_bytes = encoded_data.encode("utf-8")

    descriptor = {
        "target": did_public_key,
        "recipient": did_public_key,
        "method": "CollectionsWrite",
        "protocol": "https://identity.foundation/decentralized-web-node/protocols/credential-issuance",
        "schema": "https://identity.foundation/credential-manifest/schemas/credential-application",
        "recordId": "0474fd67-2d7e-4657-9844-3dcb8b9c54f3",
        "dataCid": get_dag_cid(data),
        "dateCreated": round(time.time() * 1000),
        "dataFormat": "application/json",
    }

    authorization = sign_as_authorization(descriptor, private_key, did_public_key)
    message = {
        "descriptor": descriptor,
        "authorization": authorization,
        "encodedData": encoded_data,
    }

    return message


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


# TODO: make this generate the same output as the dwn-relay javascript version
def get_dag_cid(data):
    cred_app_json = json.dumps(data)
    cred_app_bytes = stringToBytes(cred_app_json)

    payload_hash = multihash.digest(cred_app_bytes, "sha2-256")
    cid = make_cid(1, "dag-pb", payload_hash)
    returnStr = bytesToString(cid.encode())
    return returnStr


def sign(payload_str, private_key, did_public_key):
    protected_header = {
        "alg": "EdDSA",
        "kid": did_public_key + "#" + did_public_key.replace("did:key:", ""),
    }

    protected_header_string = json.dumps(protected_header)
    protected_header_base64_url_string = b64_url_encode(protected_header_string)

    signing_input_string = protected_header_base64_url_string + "." + payload_str

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
