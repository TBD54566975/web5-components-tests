# Web5 Component Test API

A component test server should be packaged as a container image that listens on port 8080 with an http server that implements the following endpoints

TODO: make an openapi spec of this

## meta

- `GET /health` - returns 200 when the server is ready to start the test
- `GET /shutdown` - shuts down the test server and ends the process

## VC Issuance

based on [W3C draft spec](https://w3c-ccg.github.io/vc-api/#issuing), not sure if we actually need all of these:

- `GET /credentials` list all VCs
- `GET /credentials/{id}` get a VC by ID
- `DELETE /credentials/{id}` Delete a VC
- `POST /credentials/issue` issue a credential and return it in the response body
- `POST /credentials/status` update the status of an issued credential

## VC Verificationg

- `POST /credentials/verify` verify a VC and return verificationResult
- `POST /presentations/verify` verifies a VP with or without proofs attached and returns a verificationResult in the response body
