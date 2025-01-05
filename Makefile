PYTHON = python3
PIP = pip
VENV = venv
LINTER = flake8
SORTER = isort
FORMATTER = black
TEST_DIR = tests

# Target to create a virtual environment
venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

# Install dependencies from requirements.txt
install:
	$(PIP) install -r requirements.txt

# Run isort to sort imports
sort:
	$(SORTER) .

# Lint the code using flake8
lint:
	$(LINTER) .

# Run tests (assuming pytest is used)
test:
	$(PYTHON) -m pytest $(TEST_DIR)

# Clean .pyc files
clean:
	find . -name "*.pyc" -exec rm -f {} \;

# Show help message
help:
	@echo "Available targets:"
	@echo "  venv      - Create a virtual environment"
	@echo "  install   - Install dependencies from requirements.txt"
	@echo "  sort      - Sort imports with isort"
	@echo "  format    - Format code with black (line length 120)"
	@echo "  lint      - Lint code with flake8"
	@echo "  test      - Run tests with pytest"
	@echo "  clean     - Remove all .pyc files"

test-warning:
	@pytest --disable-warnings