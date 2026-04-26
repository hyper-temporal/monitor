.PHONY: help install test demo clean explore run

help:
	@echo "Cyber Observability Tool"
	@echo ""
	@echo "Usage:"
	@echo "  make install    Install dependencies (using uv)"
	@echo "  make test       Run all tests"
	@echo "  make demo       Run demo with simulated connections"
	@echo "  make explore    Run tcpdump explorer (requires sudo)"
	@echo "  make run        Run with live capture (requires sudo + field_map.json)"
	@echo "  make clean      Remove virtual environment"
	@echo ""

install:
	uv venv
	. .venv/bin/activate && uv pip install -e .
	@echo "✓ Virtual environment created and deps installed"
	@echo "  Activate with: source .venv/bin/activate"

test:
	python -m unittest discover -s tests -p "test_*.py" -v

demo:
	python demo.py

explore:
	sudo bash explore_tcpdump.sh

run:
	@test -f field_map.json || { echo "Error: field_map.json not found"; echo "Run: make explore"; exit 1; }
	sudo python run.py --capture --field-map field_map.json

clean:
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

.DEFAULT_GOAL := help
