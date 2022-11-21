import requests
import json

endpoint = "http://localhost:8080/v1"

def create_did():
    did_json = {"keyType":"Ed25519"}
    resp = requests.put(endpoint + "/dids/key", data=json.dumps(did_json))
    return resp.json()


def create_schema():
    with open("./testdata/ssi-service/kyc-schema-input.json", "r") as file:
        schema_json = json.load(file)
    resp = requests.put(endpoint + "/schemas", data=json.dumps(schema_json))

    return resp.json()

def create_verifiable_credential():
    did = create_did()
    schema = create_schema()
    with open("./testdata/ssi-service/credential-input.json", "r") as file:
        credential_json = json.load(file)

    credential_json["issuer"] = did["did"]["id"]
    credential_json["subject"] = did["did"]["id"]
    credential_json["schema"] = schema["schema"]["id"]

    resp = requests.put(endpoint + "/credentials", data=json.dumps(credential_json))
    return resp.json()


def create_cred_manifest():
    did = create_did()
    schema = create_schema()
    with open("./testdata/ssi-service/manifest-input.json", "r") as file:
        credential_manifest = json.load(file)

    credential_manifest["issuerDID"] = did["did"]["id"]
    credential_manifest["outputDescriptors"][0]["schema"] = schema["schema"]["id"]

    resp = requests.put(endpoint + "/manifests", data=json.dumps(credential_manifest))
    return resp.json()
