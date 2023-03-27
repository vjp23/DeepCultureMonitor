FROM arm32v6/python:3.9-rc-alpine

COPY server-build/requirements.txt .

RUN pip3 install --upgrade setuptools && \
    pip3 install -r requirements.txt 

ENV PYTHONUNBUFFERED=1 \
    PORT=3141 \
    DB_NAME=/data/db/device_data.db \
    FILL_FLAG_PATH=/data/db/fill_flag.json

COPY server-src/ server-src/

WORKDIR server-src/

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 30 app:app --preload