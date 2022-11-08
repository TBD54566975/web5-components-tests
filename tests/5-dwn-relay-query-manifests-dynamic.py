import requests
from nacl.signing import SigningKey

import util

private_key = SigningKey.generate()
did_public_key = util.get_did_key_from_bytes(private_key.verify_key.encode())

message = util.create_collection_query_message(private_key, did_public_key)
messages = {"messages": [message]}

print("\nPosting to dwn-relay with payload:")
print(messages)

resp = requests.post("http://localhost:9000/", json=messages)

print("\n Recieved Response: ")
print(resp.json())

assert resp.status_code == 200
