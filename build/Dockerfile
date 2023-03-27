FROM arm32v6/python:3.9-rc-alpine

RUN apk add build-base

# Copy in the requirements.txt file
COPY build/requirements.txt .

RUN pip3 install --upgrade setuptools && \
    pip3 install -r requirements.txt 

COPY src/ src/

WORKDIR src/

# Run the loop
ENTRYPOINT ["python3", "run.py"]
