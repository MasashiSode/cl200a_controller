PYTHON_VERSION=3.8.10
WHICH_PYTHON_COMMAND=$$(which python3)
res=${WHICH_PYTHON_COMMAND}
PROJECT_NAME=cl200a_controller

install-dev:
	export WHICH_PYTHON=which python3
	pyenv local $(PYTHON_VERSION)
	poetry config virtualenvs.in-project true
	poetry env use -- $(WHICH_PYTHON_COMMAND)
	poetry install
	poetry run pre-commit install
test:
	pytest tests/ --cov=$(PROJECT_NAME) --cov-report=term-missing
