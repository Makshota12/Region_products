#!/bin/sh

KIBANA_URL="http://kibana:5601"
MAX_RETRIES=60

echo "Waiting for Kibana API..."
i=0
while [ $i -lt $MAX_RETRIES ]; do
  if curl -s "$KIBANA_URL/api/status" >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 5
done

if [ $i -ge $MAX_RETRIES ]; then
  echo "Kibana is not reachable after waiting."
  exit 1
fi

echo "Creating Kibana Data View app-logs-* ..."
curl -sS -X POST "$KIBANA_URL/api/data_views/data_view" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"data_view":{"title":"app-logs-*","name":"Application Logs","timeFieldName":"@timestamp"}}'

echo "Kibana setup complete."
