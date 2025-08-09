#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="clickhouse-dev"

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  echo "Stopping and removing container ${CONTAINER_NAME}..."
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  echo "Done."
else
  echo "No container named ${CONTAINER_NAME} found."
fi


