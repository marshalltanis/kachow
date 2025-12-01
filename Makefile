.PHONY: venv install test test-socket clean

venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with: source venv/bin/activate"

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

test:
	pytest -q

test-socket:
	pytest -q tests/test_socket_integration.py

clean:
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -type d -exec rm -rf {} +
