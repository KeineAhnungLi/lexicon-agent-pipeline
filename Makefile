.PHONY: install lint typecheck test demo audit docs

install:
	python -m pip install -e ".[dev,docs]"

lint:
	python -m ruff check .

typecheck:
	python -m mypy

test:
	python -m pytest

demo:
	python -m lexicon_pipeline --config examples/project.demo.json demo --reset

audit:
	python -m lexicon_pipeline audit-public-release --root .

docs:
	python -m mkdocs build --strict
