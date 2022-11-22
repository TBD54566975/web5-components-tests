import os
import json
import requests
import pytest

from nacl.signing import SigningKey
import dwn_util
import ssi_service_util
import util

# globals
dirname = os.path.dirname(__file__)
dwn_private_key = SigningKey.generate()
dwn_did_public_key = dwn_util.get_did_key_from_bytes(
    dwn_private_key.verify_key.encode()
)
create_did_response = None
create_schema_response = None
create_cred_manifest_response = None


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


class TestSSIServiceTestCreateCredentialManifest:
    @pytest.mark.run(order=1)
    def test_create_did(self):
        # Create a did for the issuer
        print("\nCreate a did for the issuer: ")

        with open(
            os.path.join(dirname, "fixtures/ssi-service/did-input.json"), "r"
        ) as file:
            jsonData = json.load(file)

        resp = http_request("PUT", "http://localhost:8080/v1/dids/key", jsonData)

        global create_did_response
        create_did_response = resp.json()

        assert resp.status_code == 201
        assert "did:" in create_did_response["did"]["id"]

    @pytest.mark.run(order=2)
    def test_create_schema(self):
        # Create a kyc schema for the manifest
        print("\nCreate a kyc schema for the manifest: ")

        issuer_did = create_did_response["did"]["id"]
        assert "did:" in issuer_did

        with open(
            os.path.join(dirname, "fixtures/ssi-service/kyc-schema-input.json"), "r"
        ) as file:
            jsonData = json.load(file)

        resp = http_request("PUT", "http://localhost:8080/v1/schemas", jsonData)

        global create_schema_response
        create_schema_response = resp.json()

        assert resp.status_code == 201
        assert util.is_valid_uuid(create_schema_response["id"]) == True

    @pytest.mark.run(order=3)
    def test_create_credential_manifest(self):
        # Create a credential manifest
        print("\nCreate a credential manifest: ")

        with open(
            os.path.join(dirname, "fixtures/ssi-service/manifest-input.json"), "r"
        ) as file:
            jsonData = json.load(file)

        issuer_did = create_did_response["did"]["id"]
        assert "did:" in issuer_did

        schema_id = create_schema_response["id"]
        assert schema_id is not None

        jsonData["issuerDID"] = issuer_did
        jsonData["outputDescriptors"][0]["schema"] = schema_id

        resp = http_request("PUT", "http://localhost:8080/v1/manifests", jsonData)

        global create_cred_manifest_response
        create_cred_manifest_response = resp.json()

        assert resp.status_code == 201
        assert (
            util.is_valid_uuid(
                create_cred_manifest_response["credential_manifest"]["id"]
            )
            == True
        )


class TestDWNRelayInstallProtocols:
    @pytest.mark.run(order=4)
    def test_install_protocols(self):
        # Configure Protocols for DWN-Relay
        print("\nConfigure Protocols for DWN-Relay: ")

        with open(
            os.path.join(dirname, "fixtures/dwn-relay/protocols-configure.json"), "r"
        ) as file:
            jsonData = json.load(file)

        resp = http_request("POST", "http://localhost:9000/", jsonData)

        assert resp.status_code == 200


class TestDWNRelayQueryManifestsDynamic:
    @pytest.mark.run(order=5)
    def test_query_manifests(self):
        # Query for the manifest from DWN-Relay
        message = dwn_util.create_collection_query_message(
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
    @pytest.mark.run(order=6)
    def test_submit_cred_app(self):

        cred_manifest_id = create_cred_manifest_response["credential_manifest"]["id"]
        presentation_definition_id = create_cred_manifest_response[
            "credential_manifest"
        ]["presentation_definition"]["id"]

        with open(
            os.path.join(
                dirname, "fixtures/dwn-relay/collections-write-cred-app-input.json"
            ),
            "r",
        ) as file:
            cred_app_template = json.load(file)

        cred_app_template["credential_application"]["manifest_id"] = cred_manifest_id
        cred_app_template["credential_application"]["presentation_submission"][
            "definition_id"
        ] = presentation_definition_id

        vc = ssi_service_util.create_verifiable_credential()
        cred_app_template["verifiableCredentials"] = [vc["credentialJwt"]]

        cred_app_jwt = util.create_jwt(cred_app_template, dwn_private_key.encode())

        cred_app_jwt_object = {"applicationJwt": cred_app_jwt}

        message = dwn_util.create_collection_write_message(
            dwn_private_key, dwn_did_public_key, cred_app_jwt_object
        )
        messages = {"messages": [message]}

        resp = http_request("POST", "http://localhost:9000/", messages)

        # TODO: Fix the dynamic collections write message to have the correct DAG CID
        assert resp.status_code == 200
