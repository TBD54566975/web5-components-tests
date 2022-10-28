import json
import requests
import pytest

# Make sure service is up
resp = requests.get('http://localhost:8080/readiness')
assert resp.status_code == 200

# Create a did for the issuer
print("\nCreate a did for the issuer: ")

with open("./testdata/ssi-service/did-input.json","r") as file:
    jsonData = json.load(file)

resp = requests.put('http://localhost:8080/v1/dids/key', data = json.dumps(jsonData))
print(resp.json())
assert resp.status_code == 201

issuerDID = resp.json()['did']['id']
assert "did:" in  issuerDID

# Create a kyc schema for the manifest
print("\nCreate a kyc schema for the manifest: ")

with open("./testdata/ssi-service//kyc-schema-input.json","r") as file:
    jsonData = json.load(file)

resp = requests.put('http://localhost:8080/v1/schemas', data = json.dumps(jsonData))
print(resp.json())
assert resp.status_code == 201


schemaID = resp.json()['id']
assert len(schemaID) == 36

# Create a credential manifest
print("\nCreate a credential manifest: ")

with open("./testdata/ssi-service//manifest-input.json","r") as file:
    jsonData = json.load(file)

jsonString = json.dumps(jsonData)
jsonString = jsonString.replace("<ISSUERID>", issuerDID)
jsonString = jsonString.replace("<SCHEMAID>", schemaID)

resp = requests.put('http://localhost:8080/v1/manifests', data = jsonString)
print(resp.json())
assert resp.status_code == 201