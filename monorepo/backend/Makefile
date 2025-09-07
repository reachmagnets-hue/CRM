.PHONY: dev test ingest

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

# Usage: make ingest FILE=path TENANT=site_a
ingest:
	python - <<'PY'
import os, sys
import requests

file = os.environ.get('FILE')
tenant = os.environ.get('TENANT', 'default')
admin_key = os.environ.get('ADMIN_API_KEY', 'admin_CHANGE_ME')
if not file:
    print('Provide FILE=path')
    sys.exit(1)
files = {'file': open(file, 'rb')}
headers = {'X-Admin-Key': admin_key, 'X-Tenant-Id': tenant}
r = requests.post('http://127.0.0.1:8000/api/v1/ingest/upload', files=files, headers=headers)
print(r.status_code, r.text)
PY
