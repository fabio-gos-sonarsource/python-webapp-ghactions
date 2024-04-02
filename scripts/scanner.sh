#!/bin/bash

docker run \
    --rm \
    --platform=linux/amd64 \
    --network="host" \
    -e SONAR_HOST_URL="🔥🔥🔥 PLEASE CHANGE THIS TO YOUR SONARQUBE HOST URL OR IP ADDRESS" \
    -e SONAR_SCANNER_OPTS="-Xmx8192m -Dsonar.projectKey=python-project-webapp" \
    -e SONAR_TOKEN="🔥🔥🔥 PLEASE CHANGE THIS TO YOUR CORRECT TOKEN KEY" \
    -v "$(pwd):/usr/src" \
    sonarsource/sonar-scanner-cli:latest \
    -X
