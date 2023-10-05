package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
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

func CredentialIssuance(serverURL string) error {
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
		return err
	}

	resp, err := http.Post(serverURL+"/credentials/issue", "application/json", bytes.NewReader(req))
	if err != nil {
		return err
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("incorrect status from /credential/issue: %s", resp.Status)
	}

	return nil
}

func init() {
	tests = append(tests,
		test{Name: "CredentialIssuance", Fn: CredentialIssuance},
	)
}
