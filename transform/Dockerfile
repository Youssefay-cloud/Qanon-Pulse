FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked --no-install-project

# all the files in the transform directory
COPY transform/ ./transform/

# choose the file
CMD ["python", "-m", "transform.explore"]