FROM python:3.8.10-slim

WORKDIR /app

COPY . /app

RUN apt update \
    && apt install -y --no-install-recommends ca-certificates curl firefox-esr xvfb \
    && rm -fr /var/lib/apt/lists/* \
    && mkdir -p /opt/geckodriver \
    && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz | tar xz -C /opt/geckodriver \
    && apt purge -y ca-certificates curl

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]