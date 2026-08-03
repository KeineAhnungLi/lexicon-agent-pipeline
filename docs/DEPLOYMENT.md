# Deployment

## Local package

Install with `pip install -e .` for runtime or `pip install -e ".[dev,docs]"` for contributors. The
console entry point is `lexicon-pipeline`.

## Docker

The image runs the deterministic mock demo by default:

```bash
docker build -t lexicon-agent-pipeline .
docker run --rm lexicon-agent-pipeline
docker run --rm lexicon-agent-pipeline python -m pytest
```

It intentionally contains no Codex CLI credentials. A formal Codex run is designed for an already
authenticated host. If an operator chooses to mount host tools or credentials, that is a separate
deployment decision outside this repository and must be threat-modeled.

## Documentation

`mkdocs build --strict` creates the static site. The included Pages workflow builds and deploys docs
after the repository owner enables GitHub Pages with GitHub Actions as the source. Every deployment
URL is public; inspect the content and public-data boundary before enabling deployment.
