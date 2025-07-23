#!/bin/sh
echo "Running Alembic migrations..."
PYTHONPATH=. python -m alembic upgrade head

echo "Seeding admin..."
PYTHONPATH=. python app/seed/seed_admin.py

echo "Seeding unit-agent-client..."
PYTHONPATH=. python app/seed/seed_unit_agent.py

echo "Seeding documents..."
PYTHONPATH=. python app/seed/seed_documents.py

echo "Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload