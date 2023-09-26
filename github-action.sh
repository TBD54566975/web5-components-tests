#!/bin/bash
set -exuo pipefail
cd ${GITHUB_ACTION_PATH}
docker-compose up
