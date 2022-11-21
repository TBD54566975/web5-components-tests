import unittest
import json
import requests
import pytest

from nacl.signing import SigningKey
import dwn_util
import ssi_service_util
import util

# globals
dwn_private_key = SigningKey.generate()
dwn_did_public_key = dwn_util.get_did_key_from_bytes(
    dwn_private_key.verify_key.encode()
)
create_did_response = None
create_schema_response = None
create_cred_manifest_response = None


class SSIServiceTestCreateCredentialManifest(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_create_did(self):
        # Create a did for the issuer
        print("\nCreate a did for the issuer: ")

        with open("./fixtures/ssi-service/did-input.json", "r") as file:
            jsonData = json.load(file)

        resp = requests.put(
            "http://localhost:8080/v1/dids/key", data=json.dumps(jsonData)
        )

        print("\n Recieved Response: ")
        print(resp.json())

        global create_did_response
        create_did_response = resp.json()

        self.assertEqual(resp.status_code, 201)
        self.assertIn("did:", create_did_response["did"]["id"])

    @pytest.mark.run(order=2)
    def test_create_schema(self):
        # Create a kyc schema for the manifest
        print("\nCreate a kyc schema for the manifest: ")

        issuer_did = create_did_response["did"]["id"]
        self.assertIn("did:", issuer_did)

        with open("./fixtures/ssi-service/kyc-schema-input.json", "r") as file:
            jsonData = json.load(file)

        print("\nPUT request to ssi-service with payload:")
        print(jsonData)

        resp = requests.put(
            "http://localhost:8080/v1/schemas", data=json.dumps(jsonData)
        )

        print("\n Recieved Response: ")
        print(resp.json())

        global create_schema_response
        create_schema_response = resp.json()

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(util.is_valid_uuid(create_schema_response["id"]))

    @pytest.mark.run(order=3)
    def test_create_credential_manifest(self):
        # Create a credential manifest
        print("\nCreate a credential manifest: ")

        with open("./fixtures/ssi-service/manifest-input.json", "r") as file:
            jsonData = json.load(file)

        issuer_did = create_did_response["did"]["id"]
        self.assertIn("did:", issuer_did)

        schema_id = create_schema_response["id"]
        self.assertIsNotNone(schema_id)

        jsonData["issuerDID"] = issuer_did
        jsonData["outputDescriptors"][0]["schema"] = schema_id

        print("\nPUT request to ssi-service with payload:")
        print(jsonData)

        resp = requests.put(
            "http://localhost:8080/v1/manifests", data=json.dumps(jsonData)
        )

        print("\n Recieved Response: ")
        print(resp.json())

        global create_cred_manifest_response
        create_cred_manifest_response = resp.json()

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(
            util.is_valid_uuid(
                create_cred_manifest_response["credential_manifest"]["id"]
            )
        )


class DWNRelayInstallProtocols(unittest.TestCase):
    @pytest.mark.run(order=4)
    def test_install_protocols(self):
        # Configure Protocols for DWN-Relay
        print("\nConfigure Protocols for DWN-Relay: ")

        with open("./fixtures/dwn-relay/protocols-configure.json", "r") as file:
            jsonData = json.load(file)

        print("\nPosting to dwn-relay with payload:")
        print(jsonData)

        resp = requests.post("http://localhost:9000/", json=jsonData)

        print("\n Recieved Response: ")
        print(resp.json())

        self.assertEqual(resp.status_code, 200)


class DWNRelayQueryManifestsDynamic(unittest.TestCase):
    @pytest.mark.run(order=5)
    def test_query_manifests(self):
        # Query for the manifest from DWN-Relay
        message = dwn_util.create_collection_query_message(
            dwn_private_key, dwn_did_public_key
        )
        messages = {"messages": [message]}

        print("\nPosting to dwn-relay with payload:")
        print(messages)

        resp = requests.post("http://localhost:9000/", json=messages)

        print("\n Recieved Response: ")
        print(resp.json())

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json()["replies"][0]["entries"][0]["descriptor"]["schema"],
            "https://identity.foundation/credential-manifest/schemas/credential-manifest",
        )


class DWNRelaySubmitCredApplicationDynamic(unittest.TestCase):
    @pytest.mark.run(order=6)
    def test_submit_cred_app(self):

        cred_manifest_id = create_cred_manifest_response["credential_manifest"]["id"]
        presentation_definition_id = create_cred_manifest_response[
            "credential_manifest"
        ]["presentation_definition"]["id"]

        with open(
            "./fixtures/dwn-relay/collections-write-cred-app-input.json", "r"
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

        print("\nPosting to dwn-relay with payload:")
        print(messages)

        resp = requests.post("http://localhost:9000/", json=messages)

        print("\n Recieved Response:")
        print(resp.json())

        # TODO: Fix the dynamic collections write message to have the correct DAG CID
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
