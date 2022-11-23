import os
import json
import requests
import pytest

from nacl.signing import SigningKey

from common.util import create_jwt, is_valid_uuid
from common.ssi_service_util import create_verifiable_credential
from common.dwn_util import create_collection_write_message, create_collection_query_message, get_did_key_from_bytes

dirname = os.path.dirname(__file__)

def http_request(method, url, jsonData):
    print(f"\n {method} request to url: {url} with payload:\n {jsonData}")

    if method == "PUT":
        resp = requests.put(url, json=jsonData)
    if method == "POST":
        resp = requests.post(url, json=jsonData)
    if method == "GET":
        resp = requests.get(url, json=jsonData)

    print(f"\n Recieved Response:\n {resp.json()}")

    return resp

@pytest.fixture
def dwn_private_key():
    return SigningKey.generate()

@pytest.fixture
def dwn_did_public_key(dwn_private_key):
    return get_did_key_from_bytes(
        dwn_private_key.verify_key.encode()
    )

# This will create an issuer DID in the ssi-service to be used for the creation of a credential manifest and schema
@pytest.fixture
def did():
  print("\nCreate a did for the issuer: ")

  with open(
      os.path.join(dirname, "common/fixtures/ssi-service/did-input.json"), "r"
  ) as file:
      jsonData = json.load(file)

  resp = http_request("PUT", "http://localhost:8080/v1/dids/key", jsonData)

  did_json = resp.json()

  assert resp.status_code == 201
  assert "did:" in did_json["did"]["id"]
  return did_json

# This will create a schema in the ssi-service to be used in reference to the credential manifest
@pytest.fixture
def schema(did):
    # Create a kyc schema for the manifest
    print("\nCreate a kyc schema for the manifest: ")

    issuer_did = did["did"]["id"]
    assert "did:" in issuer_did

    with open(
        os.path.join(dirname, "common/fixtures/ssi-service/kyc-schema-input.json"), "r"
    ) as file:
        jsonData = json.load(file)

    resp = http_request("PUT", "http://localhost:8080/v1/schemas", jsonData)

    create_schema_response = resp.json()

    assert resp.status_code == 201
    assert is_valid_uuid(create_schema_response["id"]) == True
    return create_schema_response


# This will create a credential manifest in the ssi-service to be applied to from a submitted credential application
@pytest.fixture(autouse=True)
def cred_manifest(did, schema):
    # Create a credential manifest
    print("\nCreate a credential manifest: ")

    with open(
        os.path.join(dirname, "common/fixtures/ssi-service/manifest-input.json"), "r"
    ) as file:
        jsonData = json.load(file)

    issuer_did = did["did"]["id"]
    assert "did:" in issuer_did

    schema_id = schema["id"]
    assert schema_id is not None

    jsonData["issuerDID"] = issuer_did
    jsonData["outputDescriptors"][0]["schema"] = schema_id

    resp = http_request("PUT", "http://localhost:8080/v1/manifests", jsonData)

    create_cred_manifest_response = resp.json()

    assert resp.status_code == 201
    assert (
        is_valid_uuid(
            create_cred_manifest_response["credential_manifest"]["id"]
        )
        == True
    )
    return create_cred_manifest_response

class TestDWNRelayInstallProtocols:
    # This test installs DWN protocols to the DWN. DWN protocols are used by the DWN to understnad what it needs to do with requests. It's basically a mapping of input route to an output route
    def test_install_protocols(self):
        # Configure Protocols for DWN-Relay
        print("\nConfigure Protocols for DWN-Relay: ")

        with open(
            os.path.join(dirname, "common/fixtures/dwn-relay/protocols-configure.json"), "r"
        ) as file:
            jsonData = json.load(file)

        resp = http_request("POST", "http://localhost:9000/", jsonData)

        assert resp.status_code == 200


class TestDWNRelayQueryManifestsDynamic:
    # This test will query the DWN for a credential manifest. The DWN will query the ssi-service for the manifest and return it to the DWN-Relay
    def test_query_manifests(self, dwn_private_key, dwn_did_public_key):
        # Query for the manifest from DWN-Relay
        message = create_collection_query_message(
            dwn_private_key, dwn_did_public_key
        )
        messages = {"messages": [message]}

        resp = http_request("POST", "http://localhost:9000/", messages)

        assert resp.status_code == 200
        assert (
            resp.json()["replies"][0]["entries"][0]["descriptor"]["schema"]
            == "https://identity.foundation/credential-manifest/schemas/credential-manifest"
        )


class TestDWNRelaySubmitCredApplicationDynamic:
    # This test will submit a credential application to the DWN. The DWN will submit the credential application to the ssi-service for the credential response containing the verifiable credential
    def test_submit_cred_app(self, cred_manifest, dwn_private_key, dwn_did_public_key):

        cred_manifest_id = cred_manifest["credential_manifest"]["id"]
        presentation_definition_id = cred_manifest[
            "credential_manifest"
        ]["presentation_definition"]["id"]

        with open(
            os.path.join(
                dirname, "common/fixtures/dwn-relay/collections-write-cred-app-input.json"
            ),
            "r",
        ) as file:
            cred_app_template = json.load(file)

        cred_app_template["credential_application"]["manifest_id"] = cred_manifest_id
        cred_app_template["credential_application"]["presentation_submission"][
            "definition_id"
        ] = presentation_definition_id

        vc = create_verifiable_credential()
        cred_app_template["verifiableCredentials"] = [vc["credentialJwt"]]

        cred_app_jwt = create_jwt(cred_app_template, dwn_private_key.encode())

        cred_app_jwt_object = {"applicationJwt": cred_app_jwt}

        message = create_collection_write_message(
            dwn_private_key, dwn_did_public_key, cred_app_jwt_object
        )
        messages = {"messages": [message]}

        resp = http_request("POST", "http://localhost:9000/", messages)

        # TODO: Fix the dynamic collections write message to have the correct DAG CID
        assert resp.status_code == 200