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

var tests = []test{}

func RunTests(serverURL string) {
	var serverAup bool

	for !serverAup {
		fmt.Println("waiting for " + serverURL + "/ready")
		resp, err := http.Get(serverURL + "/ready")
		if err != nil {
			fmt.Fprintf(os.Stderr, "waiting for test-server-a to be ready: %v\n", err)
			time.Sleep(time.Second)
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
			fmt.Fprintf(os.Stderr, "error shutting down test-server: %v\n", err)
			os.Exit(1)
		}
	}()
}
