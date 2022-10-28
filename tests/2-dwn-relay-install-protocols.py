import json
import requests
import pytest

# Configure Protocols for DWN-Relay
print("\nConfigure Protocols for DWN-Relay: ")

with open("./testdata/dwn-relay/protocols-configure.json","r") as file:
    jsonData = json.load(file)

print("\nPosting to dwn-relay with payload:")
print(jsonData)

resp = requests.post('http://localhost:9000/', json = jsonData)

print("\n Recieved Response: ")
print(resp.json())

assert resp.status_code == 200
assert resp.json()['replies'][0]['status']['detail'] == 'Accepted'