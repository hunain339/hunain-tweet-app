#!/usr/bin/env bash
set -euo pipefail

# Smoke-test script: creates an isolated venv, installs requirements-prod.txt,
# runs `manage.py check` and a subset of tests for the `tweet` app.

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$HERE/.." && pwd)
VENV_DIR="/tmp/django_prod_test_venv_$(date +%s)"

echo "Repo: $REPO_ROOT"
echo "Creating venv at: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
echo "Installing runtime dependencies from requirements-prod.txt"
pip install -r "$REPO_ROOT/requirements-prod.txt"

echo "Running Django checks"
cd "$REPO_ROOT"
python manage.py check

echo "Running subset tests: app 'tweet'"
python manage.py test tweet --keepdb

echo "Smoke-test completed successfully. To re-run, execute: $REPO_ROOT/scripts/smoke_test_prod_requirements.sh"

deactivate || true
