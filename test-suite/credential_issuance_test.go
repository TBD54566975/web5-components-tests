package testsuite_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"
)

// {
// 	"@context": [
// 	  "https://www.w3.org/2018/credentials/v1",
// 	],
// 	"id": "{{ID}}",
// 	"type": [
// 	  "VerifiableCredential"
// 	],
// 	"issuer": "{{ISSUER}}",
// 	"issuanceDate": "{{DATE}}",
// 	"credentialSubject": {
// 	  "id": "{{SUBJECT}}",
// 	  "firstName": "bob"
// 	}

// todo: better struct names all around
type CredentialIssuanceRequest struct {
	Credential CredentialIssuanceRequestCredential `json:"credential"`
	Options    CredentialIssuanceRequestOptions    `json:"options"`
}

type CredentialIssuanceRequestCredential struct {
	Context           []string       `json:"@context"`
	ID                string         `json:"id"`
	Type              []string       `json:"type"`
	Issuer            string         `json:"issuer"`
	IssuanceDate      string         `json:"issuanceDate"`
	CredentialSubject map[string]any `json:"credentialSubject"`
}

type CredentialIssuanceRequestOptions struct {
}

func TestCredentialIssuance(t *testing.T) {
	req, err := json.Marshal(CredentialIssuanceRequest{
		Credential: CredentialIssuanceRequestCredential{
			Context:      []string{"https://www.w3.org/2018/credentials/v1"},
			ID:           "???",
			Type:         []string{"VerifiableCredential"},
			Issuer:       "????",
			IssuanceDate: "???",
			CredentialSubject: map[string]any{
				"id":        "????",
				"firstName": "bob",
			},
		},
	})
	if err != nil {
		t.Error(err)
		return
	}

	resp, err := http.Post(testServerURL+"/credentials/issue", "application/json", bytes.NewReader(req))
	if err != nil {
		t.Error(err)
		return
	}

	if resp.StatusCode != http.StatusOK {
		t.Error("incorrect status from /credential/issue: ", resp.Status)
		return
	}
}
