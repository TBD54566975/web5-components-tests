package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
)

// todo: better struct names all around
type CredentialIssuanceRequest struct {
	Credential CredentialIssuanceRequestCredential `json:"credential"`
}

type CredentialIssuanceRequestCredential struct {
	Context           []string       `json:"@context"`
	ID                string         `json:"id"`
	Type              []string       `json:"type"`
	Issuer            string         `json:"issuer"`
	CredentialSubject map[string]any `json:"credentialSubject"`
}

func CredentialIssuanceTest(serverURL string) error {
	expectedContext := []string{"https://www.w3.org/2018/credentials/v1"}
	expectedType := []string{"VerifiableCredential"}
	expectedID := "id-123"
	expectedIssuer := "did:example:123"
	expectedCredentialSubject := map[string]interface{}{
		"id":        "did:example:123",
		"firstName": "bob",
	}

	req, err := json.Marshal(CredentialIssuanceRequest{
		Credential: CredentialIssuanceRequestCredential{
			Context:           expectedContext,
			ID:                expectedID,
			Type:              expectedType,
			Issuer:            expectedIssuer,
			CredentialSubject: expectedCredentialSubject,
		},
	})

	if err != nil {
		return err
	}

	resp, err := http.Post(serverURL+"/credentials/unsigned", "application/json", bytes.NewReader(req))
	if err != nil {
		return err
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("incorrect status from /credential/issue: %s", resp.Status)
	}

	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}

	var jsonData map[string]interface{}
	err = json.Unmarshal(bodyBytes, &jsonData)
	if err != nil {
		log.Fatalf("Error decoding JSON: %v", err)
	}

	// Check @context
	if context, ok := jsonData["@context"].([]interface{}); !ok || !compareStringSlices(context, expectedContext) {
		return fmt.Errorf("Assertion failed for @context. Expected %v, got %v", expectedContext, context)
	}

	// Check type
	if typeValue, ok := jsonData["type"].([]interface{}); !ok || !compareStringSlices(typeValue, expectedType) {
		return fmt.Errorf("Assertion failed for type. Expected %v, got %v", expectedType, typeValue)
	}

	// Check id
	if id, ok := jsonData["id"].(string); !ok || id != expectedID {
		return fmt.Errorf("Assertion failed for id. Expected %s, got %s", expectedID, id)
	}

	// Check issuer
	if issuer, ok := jsonData["issuer"].(string); !ok || issuer != expectedIssuer {
		return fmt.Errorf("Assertion failed for issuer. Expected %s, got %s", expectedIssuer, issuer)
	}

	// Check credentialSubject
	if cs, ok := jsonData["credentialSubject"].(map[string]interface{}); !ok || !compareMaps(cs, expectedCredentialSubject) {
		return fmt.Errorf("Assertion failed for credentialSubject. Expected %v, got %v", expectedCredentialSubject, cs)
	}

	println("Finished cred issuance test")

	return nil
}

func compareStringSlices(a []interface{}, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i, v := range a {
		if vs, ok := v.(string); !ok || vs != b[i] {
			return false
		}
	}
	return true
}

// Utility function to compare maps
func compareMaps(a, b map[string]interface{}) bool {
	for k, v := range a {
		if b[k] != v {
			return false
		}
	}
	return true
}
