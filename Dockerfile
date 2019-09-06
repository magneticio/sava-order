FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8 as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

RUN pip install --install-option="--prefix=/install" elasticsearch

FROM base

COPY --from=builder /install /usr/local

COPY ./app /app

