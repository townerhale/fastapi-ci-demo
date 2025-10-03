#!/usr/bin/env bash
# tests/test_docker_build.sh
# Validate that the Docker image builds successfully.
# Usage:
#   ./tests/test_docker_build.sh
# Optional env vars:
#   TAG=fastapi-ci-demo:build-test
#   DOCKERFILE=Dockerfile
#   CONTEXT=.

set -Eeuo pipefail

TAG="${TAG:-fastapi-ci-demo:build-test}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
CONTEXT="${CONTEXT:-.}"

echo "==> Validating Docker build"
echo "    Dockerfile: $DOCKERFILE"
echo "    Context:    $CONTEXT"
echo "    Tag:        $TAG"

# Basic preflight checks
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found on PATH." >&2
  exit 127
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker engine is not running." >&2
  exit 1
fi

# Build the image (fails the script if the build fails)
docker build -f "$DOCKERFILE" -t "$TAG" "$CONTEXT"

echo "✅ Docker build succeeded: $(docker images -q "$TAG" | head -n1)"
