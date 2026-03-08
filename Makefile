# Lattice Project Management

.PHONY: setup start-infra stop-infra test test-verbose run-api run-frontend lint clean

# Initial setup: Create venv and install dependencies
setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	cd frontend && npm install

# Start Memgraph and Redis
start-infra:
	docker-compose up -d memgraph redis

# Stop all docker services
stop-infra:
	docker-compose down

# Run all integration tests
test: start-infra
	PYTHONPATH=. ./venv/bin/pytest ai_integration_test/

# Run tests with verbose output
test-verbose: start-infra
	PYTHONPATH=. ./venv/bin/pytest -v ai_integration_test/

# Run the FastAPI backend
run-api: start-infra
	PYTHONPATH=. ./venv/bin/uvicorn app.main:app --reload

# Run the React frontend
run-frontend:
	cd frontend && npm run dev

# Run all linters and formatters
lint:
	./venv/bin/black . --exclude venv
	PYTHONPATH=. ./venv/bin/mypy --explicit-package-bases app/ --ignore-missing-imports
	cd frontend && npx prettier --write . && npm run build

# Clean up temporary files
clean:
	rm -rf venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
