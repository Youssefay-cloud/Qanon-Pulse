FROM apache/airflow:3.2.2

USER root
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

USER airflow
WORKDIR /home/airflow/project

# A separate virtual environment for OUR scripts, built from your lock file
ENV UV_PROJECT_ENVIRONMENT=/home/airflow/pipeline-venv
COPY --chown=airflow pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-install-project --no-dev