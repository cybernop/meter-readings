FROM ghcr.io/astral-sh/uv:alpine

# RUN apk add --no-cache python3 uv

WORKDIR /app

COPY src .
COPY pyproject.toml .
COPY uv.lock .

RUN uv tool install .

ENTRYPOINT [ "meter_readings", "--config", "/data/readings-config.yaml" ]
