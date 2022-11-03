import json
import requests
import pytest

# TODO: This needs to be a dynamic payload because the static payload references a manifest which does not exist
# Submit Credential Applicaiton
print("Submit Credential Applicaiton: ")

with open("./testdata/dwn-relay/collections-write-input.json", "r") as file:
    jsonData = json.load(file)

print("\nPosting to dwn-relay with payload:")
print(jsonData)

resp = requests.post("http://localhost:9000/", json=jsonData)

print("\n Recieved Response: ")
print(resp.json())

assert resp.status_code == 200
