package testsuite_test

import (
	"fmt"
	"net/http"
	"os"
	"testing"
	"time"
)

const testServerURL = "http://test-server:8080"

func TestMain(m *testing.M) {
	var serverAup bool

	for !serverAup {
		fmt.Println("waiting for " + testServerURL + "/ready")
		resp, err := http.Get(testServerURL + "/ready")
		if err != nil {
			fmt.Fprintf(os.Stderr, "waiting for test-server-a to be ready: %v\n", err)
			continue
		} else {
			if resp.StatusCode == http.StatusOK {
				serverAup = true
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

	status := m.Run()

	if _, err := http.Get(testServerURL + "/shutdown"); err != nil {
		fmt.Fprintf(os.Stderr, "error shutting down test-server: %v\n", err)
		os.Exit(1)
	}

	os.Exit(status)
}
