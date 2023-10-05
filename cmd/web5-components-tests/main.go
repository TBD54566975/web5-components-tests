package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"

	"github.com/TBD54566975/web5-components-tests/tests"
)

var (
	testOnly = flag.Bool("test-only", false, "when set, the server is not built and is expected to be already running")
	server   = flag.String("server", "http://localhost:8080", "url of the server to connect to")
)

func main() {
	flag.Parse()
	if !*testOnly {
		cmd := exec.Command("docker", "build", "-t", "web5-component:latest", "-f", ".web5-component/test.Dockerfile", ".")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			panic(err)
		}

		cmd = exec.Command("docker", "run", "-p", "8080:8080", "--rm", "web5-component:latest")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Start(); err != nil {
			panic(err)
		}

		defer func() {
			fmt.Println("shutting down server")
			if err := cmd.Process.Signal(os.Kill); err != nil {
				panic(err)
			}
			if err := cmd.Wait(); err != nil {
				panic(err)
			}
		}()
	}

	tests.RunTests(*server)
}
