# System Test

To orchestrate end to end testing of Web5 components.

## Running System Test Locally

1. Clone the repo
   `git clone https://github.com/TBD54566975/system-test.git`

2. Spin up the ssi-service and dwn-relay. \* Note is is important to use --no cache because if you don't it will not use the latest version of mainline
   `docker-compose build --no-cache && docker-compose up`

3. Run a test script in the tests directory. To run all tests run:
   `python 0-all-tests.py`

## Project Resources

| Resource                                   | Description                                                                   |
| ------------------------------------------ | ----------------------------------------------------------------------------- |
| [CODEOWNERS](./CODEOWNERS)                 | Outlines the project lead(s)                                                  |
| [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | Expected behavior for project contributors, promoting a welcoming environment |
| [CONTRIBUTING.md](./CONTRIBUTING.md)       | Developer guide to build, test, run, access CI, chat, discuss, file issues    |
| [GOVERNANCE.md](./GOVERNANCE.md)           | Project governance                                                            |
| [LICENSE](./LICENSE)                       | Apache License, Version 2.0                                                   |
