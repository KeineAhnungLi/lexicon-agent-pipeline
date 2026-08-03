FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY prompts ./prompts
COPY schemas ./schemas
COPY examples ./examples
COPY tests ./tests

RUN python -m pip install --no-cache-dir ".[dev]"

CMD ["lexicon-pipeline", "--config", "examples/project.demo.json", "demo", "--reset"]
