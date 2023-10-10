package tests

import (
	"fmt"
	"net/http"
	"os"
	"time"

	"golang.org/x/exp/slog"
)

type test struct {
	Name string
	Fn   func(serverURL string) error
}

var tests = []test{
	{Name: "CredentialIssuance", Fn: CredentialIssuanceTest},
}

func RunTests(serverURL string) {
	var serverAup bool

	for !serverAup {
		readyURL := serverURL + "/ready"
		resp, err := http.Get(readyURL)
		if err != nil {
			slog.Debug("waiting for server to be ready", "url", readyURL, "err", err)
			time.Sleep(time.Second)
			continue
		} else {
			if resp.StatusCode == http.StatusOK {
				serverAup = true
				slog.Debug("server is ready", "url", readyURL)
			}
		}

		// resp, err = http.Get("http://test-server-b:8080/ready")
		// if err != nil {
		// 	fmt.Fprintf(os.Stderr, "waiting for test-server-b to be ready: %v", err)
		// 	continue
		// } else {
		// 	if resp.StatusCode == http.StatusOK {
		// 		serverBup = true
		// 	}
		// }

		time.Sleep(time.Second)
	}

	success := true
	for _, t := range tests {
		slog.Info("running", "test", t.Name)
		if err := t.Fn(serverURL); err != nil {
			slog.Error("error", "test", t.Name, "error", err)
			success = false
		}
	}

	if !success {
		os.Exit(1)
	}

	defer func() {
		if _, err := http.Get(serverURL + "/shutdown"); err != nil {
			// fmt.Fprintf(os.Stderr, "error shutting down test-server: %v\n", err)
			slog.Error("error shutting down server", "error", err)
			os.Exit(1)
		}
	}()
}

func compareStringSlices(actual []string, expected []string, field string) error {
	if len(actual) != len(expected) {
		return fmt.Errorf("incorrect value for %s: expected %v, got %v", field, expected, actual)
	}

	for i, v := range actual {
		if v != expected[i] {
			return fmt.Errorf("incorrect value for %s: expected %v, got %v", field, expected, actual)
		}
	}
	return nil
}

// Utility function to compare maps
func compareMaps(actual, expected map[string]interface{}, field string) error {
	for k, v := range expected {
		if actual[k] != v {
			return fmt.Errorf("incorrect value for %s: expected %v, got %v", field, expected, actual)
		}
	}
	return nil
}

func compareStrings(actual string, expected string, field string) error {
	if actual != expected {
		return fmt.Errorf("incorrect value for %s: expected %v, got %v", field, expected, actual)
	}
	return nil
}
