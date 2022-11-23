# Web5 Components Tests

To orchestrate end to end testing of Web5 components.

This repo contains a docker-compose file which pulls down and spins up the latest components from the WEB5 stack. It then test suites against the endpoints of these services.

![system test architecture](docs/testarch.png)

## Running System Test Locally

1. Clone the repo
   `git clone https://github.com/TBD54566975/web5-components-tests.git`

2. Spin up the ssi-service and dwn-relay. \* Note is is important to use --no cache because if you don't it will not use the latest version of mainline
   `docker-compose build --no-cache && docker-compose up`

3. In a new shell navigate to web5-components-tests/tests and run a test script in the tests directory. To run all tests run:
   `cd tests`
   `pip install -r requirements.txt`
   `python 0-all-tests.py`

## Automatic Runs Via Github Actions

When a new verion of a web5 component is pushed up the github action pulls down and spins up the latest components from the WEB5 stack and runs tests against them. The github actions can be seen here - https://github.com/TBD54566975/system-test/actions

## Project Resources

| Resource                                   | Description                                                                   |
| ------------------------------------------ | ----------------------------------------------------------------------------- |
| [CODEOWNERS](./CODEOWNERS)                 | Outlines the project lead(s)                                                  |
| [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | Expected behavior for project contributors, promoting a welcoming environment |
| [CONTRIBUTING.md](./CONTRIBUTING.md)       | Developer guide to build, test, run, access CI, chat, discuss, file issues    |
| [GOVERNANCE.md](./GOVERNANCE.md)           | Project governance                                                            |
| [LICENSE](./LICENSE)                       | Apache License, Version 2.0                                                   |
