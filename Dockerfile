FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /bin/uv

ENV UV_PYTHON_DOWNLOADS=never \
    UV_NO_CACHE=1 \
    PATH="/service/.venv/bin:${PATH}"
WORKDIR /service

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY app ./app
COPY model ./model

RUN useradd --create-home --uid 10001 api
USER api

EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8000}\" --workers 1"]
