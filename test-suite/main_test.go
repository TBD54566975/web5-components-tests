package testsuite_test

import (
	"fmt"
	"net/http"
	"os"
	"testing"
	"time"
)

func TestMain(m *testing.M) {
	var serverAup bool

	for !serverAup {
		resp, err := http.Get("http://test-server-a:8080/ready")
		if err != nil {
			fmt.Fprintf(os.Stderr, "waiting for test-server-a to be ready: %v", err)
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
		fmt.Println("waiting for both servers to start")
	}

	status := m.Run()

	for _, server := range []string{"test-server-a"} {
		if _, err := http.Get(fmt.Sprintf("http://%s:8080/shutdown", server)); err != nil {
			fmt.Fprintf(os.Stderr, "error shutting down %s: %v", server, err)
			os.Exit(1)
		}
	}

	os.Exit(status)
}

func TestCreateVC(t *testing.T) {
	fmt.Println("pass")
}
