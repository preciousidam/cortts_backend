# Makefile for Cortts FastAPI Backend

PYTHONPATH=.

# Alembic commands using Python module
migrate:
	PYTHONPATH=$(PYTHONPATH) python -m alembic revision --autogenerate -m "auto"

upgrade:
	PYTHONPATH=$(PYTHONPATH) python -m alembic upgrade head

downgrade:
	PYTHONPATH=$(PYTHONPATH) python -m alembic downgrade -1

show:
	PYTHONPATH=$(PYTHONPATH) python -m alembic current

history:
	PYTHONPATH=$(PYTHONPATH) python -m alembic history --verbose

# Start server (uvicorn)
run:
	python -m uvicorn app.main:app --host 0.0.0.0 --reload

# Clean up pycaches
clean:
	find . -type d -name __pycache__ -exec rm -r {} +

tree:
	@echo "Directory structure:"
	@tree -I '__pycache__|*.pyc|*.pyo|*.pyd|venv|.venv|.git|node_modules|dist|build|*.egg-info' -L 10 > tree.txt

# Test DB connection
check-db:
	PYTHONPATH=$(PYTHONPATH) python -c "from app.db.session import engine; print(engine.connect())"

seed-unit-agent-client:
	PYTHONPATH=$(PYTHONPATH) python app/seed/seed_unit_agent.py

seed-docs:
	PYTHONPATH=$(PYTHONPATH) python app/seed/seed_documents.py

seed-admin:
	PYTHONPATH=$(PYTHONPATH) python app/seed/seed_admin.py

seed-all:
	make seed-admin && make seed-unit-agent-client && make seed-docs

test:
	PYTHONPATH=$(PYTHONPATH) python -m pytest -v