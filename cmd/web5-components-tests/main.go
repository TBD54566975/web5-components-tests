package main

import (
	"flag"
	"os"
	"os/exec"

	"github.com/TBD54566975/web5-components-tests/tests"
	"golang.org/x/exp/slog"
)

var (
	testOnly     = flag.Bool("test-only", true, "when set, the server is not built and is expected to be already running")
	jsServer     = flag.String("js-server", "http://localhost:8080", "url of the server to connect to")
	kotlinServer = flag.String("kotlin-server", "http://localhost:8081", "url of the server to connect to")
)

func main() {
	flag.Parse()

	logger := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug})
	slog.SetDefault(slog.New(logger))

	if !*testOnly {
		cmd := exec.Command("docker", "build", "-t", "web5-component:latest", "-f", ".web5-component/test.Dockerfile", ".")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			slog.Error("error building server", "error", err)
			os.Exit(1)
		}

		cmd = exec.Command("docker", "run", "-p", "8080:8080", "--rm", "web5-component:latest")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Start(); err != nil {
			slog.Error("error running server", "error", err)
			os.Exit(1)
		}

		defer func() {
			slog.Debug("shutting down server")
			if err := cmd.Process.Signal(os.Kill); err != nil {
				panic(err)
			}
			if err := cmd.Wait(); err != nil {
				panic(err)
			}
		}()
	}

	tests.RunTests(*jsServer)
	tests.RunTests(*kotlinServer)
}
