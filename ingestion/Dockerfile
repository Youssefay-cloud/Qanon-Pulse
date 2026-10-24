FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

# These are now relative to the ROOT folder
COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked --no-install-project

# Notice the 'ingestion/' prefix here!
COPY ingestion/ingest.py .

ENTRYPOINT ["python", "ingest.py"]