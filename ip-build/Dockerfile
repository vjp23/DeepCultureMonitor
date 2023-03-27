FROM python:3.9-bullseye

COPY ip-build/requirements.txt .
COPY ip-build/pip.conf /etc/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV LOG_FILENAME=/data/logs/ip_logs.log \
    UPDATE_IP_EVERY=30 \
    GOOGLE_APPLICATION_CREDENTIALS=petaccio-52c6b733ccf8.json

COPY ip-src/ ip-src/

WORKDIR ip-src/

ENTRYPOINT ["python3", "publish_public_ip.py"]