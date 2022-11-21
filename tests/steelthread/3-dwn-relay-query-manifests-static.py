import json
import requests
import pytest

# Query Credential Manifests
print("\nQuery Credential Manifests: ")

with open("./testdata/dwn-relay/collections-query-input.json", "r") as file:
    jsonData = json.load(file)

print("\nPosting to dwn-relay with payload:")
print(jsonData)

resp = requests.post("http://localhost:9000/", json=jsonData)

print("\n Recieved Response: ")
print(resp.json())

assert resp.status_code == 200
