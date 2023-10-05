package main

import (
	"flag"
	"os"
	"os/exec"

	"github.com/TBD54566975/web5-components-tests/tests"
	"golang.org/x/exp/slog"
)

var (
	nostart = flag.Bool("no-start", false, "when set, the server is not built and is expected to be already running")
	nostop  = flag.Bool("no-stop", false, "when set, the server is not asked to shut down")
	server  = flag.String("server", "http://localhost:8080", "url of the server to connect to")
)

func main() {
	flag.Parse()

	dir, _ := os.Getwd()
	if len(flag.Args()) > 0 {
		dir = flag.Arg(0)
	}

	logger := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug})
	slog.SetDefault(slog.New(logger))

	if !*nostart {
		cmd := exec.Command("docker", "build", "-t", "web5-component:latest", "-f", ".web5-component/test.Dockerfile", ".")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Dir = dir
		if err := cmd.Run(); err != nil {
			slog.Error("error building server", "error", err)
			os.Exit(1)
		}

		cmd = exec.Command("docker", "run", "-p", "8080:8080", "--rm", "web5-component:latest")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Dir = dir
		if err := cmd.Start(); err != nil {
			slog.Error("error running server", "error", err)
			os.Exit(1)
		}

		if !*nostop {
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
	}

	tests.RunTests(*server)
}
