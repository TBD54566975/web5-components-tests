import requests
from nacl.signing import SigningKey

import dwn_util
import ssi_service_util

import json
import requests
import pytest


print("Submit Credential Applicaiton: ")

private_key = SigningKey.generate()
did_public_key = dwn_util.get_did_key_from_bytes(private_key.verify_key.encode())

cred_manifest_resp = requests.get("http://localhost:8080/v1/manifests")
assert cred_manifest_resp.status_code == 200

cred_manifest_id = cred_manifest_resp.json()["manifests"][0]["credential_manifest"]["id"]
presentation_definition_id = cred_manifest_resp.json()["manifests"][0]["credential_manifest"]["presentation_definition"]["id"]

with open("./testdata/dwn-relay/collections-write-cred-app-input.json", "r") as file:
    cred_app_template = json.load(file)

cred_app_template["credential_application"]["manifest_id"] = cred_manifest_id
cred_app_template["credential_application"]["presentation_submission"]["definition_id"] = presentation_definition_id

vc = ssi_service_util.create_verifiable_credential()
cred_app_template["verifiableCredentials"] = [vc["credentialJwt"]]

cred_app_jwt = dwn_util.create_jwt(cred_app_template, private_key.encode())

cred_app_jwt_object = { "applicationJwt": cred_app_jwt }

message = dwn_util.create_collection_write_message(private_key, did_public_key, cred_app_jwt_object)
messages = {"messages": [message]}

print("\nPosting to dwn-relay with payload:")
print(messages)

resp = requests.post("http://localhost:9000/", json=messages)

print("\n Recieved Response: ")
print(resp.json())

# assert resp.status_code == 200