#!/usr/bin/env bash
set -euo pipefail

# Start an ephemeral ClickHouse in Docker, create table default.user_events,
# and populate it with 150 sample events matching the reference Kafka schema.

CONTAINER_NAME="clickhouse-dev"
IMAGE="clickhouse/clickhouse-server:latest"
HTTP_URL="http://localhost:8123"
# ClickHouse credentials
CH_USER="dev"
CH_PASSWORD="dev"

echo "Ensuring no existing container named ${CONTAINER_NAME} is running..."
if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

echo "Starting ClickHouse container (${CONTAINER_NAME})..."
docker run -d --rm \
  --name "${CONTAINER_NAME}" \
  -p 8123:8123 -p 9000:9000 \
  --ulimit nofile=262144:262144 \
  -e CLICKHOUSE_USER="${CH_USER}" \
  -e CLICKHOUSE_PASSWORD="${CH_PASSWORD}" \
  -e CLICKHOUSE_DB="default" \
  "${IMAGE}" >/dev/null

echo "Waiting for ClickHouse HTTP port to be ready..."
for i in {1..60}; do
  if curl -s "${HTTP_URL}/ping" | grep -q "Ok."; then
    echo "ClickHouse is ready."
    break
  fi
  sleep 1
  if [[ "$i" -eq 60 ]]; then
    echo "ClickHouse did not become ready in time." >&2
    exit 1
  fi
done

run_sql() {
  local sql="$1"
  curl -sS -u "${CH_USER}:${CH_PASSWORD}" "${HTTP_URL}" --data-binary "$sql" | cat
}

echo "Creating table default.user_events..."
run_sql "DROP TABLE IF EXISTS default.user_events;"
run_sql "
CREATE TABLE default.user_events (
  user_id String,
  timestamp DateTime,
  event String,
  page String,
  element String,
  form String,
  query String,
  product_id String,
  order_id String,
  source String,
  method String,
  session_id String,
  referrer String,
  device String
) ENGINE = MergeTree() ORDER BY (timestamp, user_id);
"

echo "Generating 150 sample events and inserting into default.user_events..."
python3 - <<'PY' | curl -sS -u "${CH_USER}:${CH_PASSWORD}" -H 'Content-Type: application/json' --data-binary @- "${HTTP_URL}/?query=INSERT%20INTO%20default.user_events%20FORMAT%20JSONEachRow" | cat
import json
import random
from datetime import datetime, timedelta

EVENT_TYPES = [
    "page_view", "button_click", "form_submit", "search",
    "add_to_cart", "remove_from_cart", "purchase", "signup", "login"
]
PAGES = ["/dashboard", "/products", "/cart", "/checkout"]
ELEMENTS = ["add_to_cart", "checkout_btn", "login_btn", "N/A"]
FORMS = ["login", "registration", "N/A"]
QUERIES = ["product", "category", "N/A"]
PRODUCT_IDS = ["prod_123", "prod_456", "N/A"]
ORDER_IDS = ["order_789", "N/A"]
SOURCES = ["organic", "N/A"]
METHODS = ["email", "N/A"]
REFERRERS = ["google.com", "facebook.com", "twitter.com", "direct", "N/A"]
DEVICES = ["desktop", "mobile", "tablet"]

user_ids = [f"user_{i:03d}" for i in range(1, 51)]

def generate_event():
    event_type = random.choice(EVENT_TYPES)
    user_id = random.choice(user_ids)
    ts = datetime.now() - timedelta(
        hours=random.randint(0, 24),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    # Format for ClickHouse DateTime
    timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
    session_id = f"session_{random.randint(1000, 9999)}"
    referrer = random.choice(REFERRERS)
    device = random.choice(DEVICES)

    page = random.choice(PAGES) if event_type == "page_view" else "N/A"
    element = random.choice(ELEMENTS) if event_type == "button_click" else "N/A"
    form = random.choice(FORMS) if event_type == "form_submit" else "N/A"
    query = random.choice(QUERIES) if event_type == "search" else "N/A"
    product_id = random.choice(PRODUCT_IDS) if event_type in ["add_to_cart", "remove_from_cart"] else "N/A"
    order_id = random.choice(ORDER_IDS) if event_type == "purchase" else "N/A"
    source = random.choice(SOURCES) if event_type == "signup" else "N/A"
    method = random.choice(METHODS) if event_type == "login" else "N/A"

    return {
        "user_id": user_id,
        "timestamp": timestamp,
        "event": event_type,
        "page": page,
        "element": element,
        "form": form,
        "query": query,
        "product_id": product_id,
        "order_id": order_id,
        "source": source,
        "method": method,
        "session_id": session_id,
        "referrer": referrer,
        "device": device,
    }

for _ in range(150):
    print(json.dumps(generate_event()))
PY

echo "Verifying row count..."
run_sql "SELECT count() FROM default.user_events;"

echo "All set. ClickHouse is running in Docker with 150 sample rows in default.user_events."
echo "HTTP: ${HTTP_URL}/play | Container: ${CONTAINER_NAME}"


