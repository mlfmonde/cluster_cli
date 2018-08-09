FROM python:3.7-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir .

ENTRYPOINT ["cluster"]
CMD ["-h"]
