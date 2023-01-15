.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "format - format files to match code style using black"
	@echo "install - install dependencies"
	@echo "test - run tests"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	black --check .

format:
	black .

install: clean
	pip install --editable .

install-dev: install
	pip install -r requirements-dev.txt

test:
	brownie test --network eth-mainnet-fork -s
